#!/bin/bash
set -e

# All output goes to stdout/stderr for Kubernetes logging
exec 2>&1

export OPSML_SERVER_PORT=${OPSML_SERVER_PORT:-8000}
export APP_ENV=${APP_ENV:-staging}

if ! [[ "$OPSML_SERVER_PORT" =~ ^[0-9]+$ ]]; then
    echo "$(date): ERROR: OPSML_SERVER_PORT must be numeric, got: $OPSML_SERVER_PORT"
    exit 1
fi


# PID tracking
RUST_API_PID=""
SVELTEKIT_PID=""
NGINX_PID=""

# Cleanup function
cleanup() {
    echo "$(date): Received shutdown signal, cleaning up..."
    
    # Graceful shutdown in reverse order
    if [[ -n "$NGINX_PID" ]]; then
        echo "$(date): Stopping NGINX..."
        kill -QUIT $NGINX_PID 2>/dev/null || true
    fi
    
    if [[ -n "$SVELTEKIT_PID" ]]; then
        echo "$(date): Stopping SvelteKit..."
        kill -TERM $SVELTEKIT_PID 2>/dev/null || true
    fi
    
    if [[ -n "$RUST_API_PID" ]]; then
        echo "$(date): Stopping Rust API..."
        kill -TERM $RUST_API_PID 2>/dev/null || true
    fi
    
    # Wait for graceful shutdown
    sleep 5
    
    # Force kill if still running
    for pid in $NGINX_PID $SVELTEKIT_PID $RUST_API_PID; do
        if [[ -n "$pid" ]] && kill -0 $pid 2>/dev/null; then
            echo "$(date): Force killing process $pid"
            kill -KILL $pid 2>/dev/null || true
        fi
    done
    
    echo "$(date): Cleanup complete"
    exit 0
}

# Set up signal handlers for Kubernetes
trap cleanup SIGTERM SIGINT

# Wait for service function
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "$(date): Waiting for $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            echo "$(date): $service_name is ready on port $port"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "$(date): Still waiting for $service_name (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "$(date): ERROR: $service_name failed to start on port $port after $max_attempts attempts"
    return 1
}

# echo app env
echo "$(date): Starting OpsML in APP_ENV=${APP_ENV}"

# update nginx template
echo "$(date): Configuring NGINX..."
if ! envsubst '${OPSML_SERVER_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf; then
    echo "$(date): ERROR: Failed to process NGINX template"
    exit 1
fi

# Start Rust API server
echo "$(date): Starting Rust API server on port ${OPSML_SERVER_PORT}..."
/usr/local/bin/opsml-server &
RUST_API_PID=$!
echo "$(date): Rust API PID: $RUST_API_PID"

# Wait for Rust API
if ! wait_for_service ${OPSML_SERVER_PORT} "Rust API"; then
    echo "$(date): Failed to start Rust API, exiting..."
    exit 1
fi

# Start SvelteKit server
echo "$(date): Starting SvelteKit server on port 3000..."
cd /app/ui
PORT=3000 NODE_ENV=production node build/index.js &
SVELTEKIT_PID=$!
echo "$(date): SvelteKit PID: $SVELTEKIT_PID"

# Wait for SvelteKit
if ! wait_for_service 3000 "SvelteKit"; then
    echo "$(date): Failed to start SvelteKit, exiting..."
    exit 1
fi

# Start NGINX
echo "$(date): Testing NGINX configuration..."
if ! nginx -t; then
    echo "$(date): NGINX configuration test failed, exiting..."
    exit 1
fi

echo "$(date): Starting NGINX on port ${OPSML_SERVER_PORT}..."
nginx -g "daemon off;" &
NGINX_PID=$!
echo "$(date): NGINX PID: $NGINX_PID"

# Wait for NGINX
if ! wait_for_service "${OPSML_SERVER_PORT}" "NGINX"; then
    echo "$(date): Failed to start NGINX, exiting..."
    exit 1
fi

echo "$(date): All services started successfully"
echo "$(date): Rust API: $RUST_API_PID, SvelteKit: $SVELTEKIT_PID, NGINX: $NGINX_PID"

# Process monitoring loop
while true; do
    # Check if any process has died
    for pid_name in "RUST_API_PID:Rust API" "SVELTEKIT_PID:SvelteKit" "NGINX_PID:NGINX"; do
        pid_var=$(echo $pid_name | cut -d: -f1)
        service_name=$(echo $pid_name | cut -d: -f2)
        pid_value=$(eval echo \$$pid_var)
        
        if [[ -n "$pid_value" ]] && ! kill -0 $pid_value 2>/dev/null; then
            echo "$(date): ERROR: $service_name (PID: $pid_value) has died unexpectedly"
            cleanup
            exit 1
        fi
    done
    
    sleep 10
done