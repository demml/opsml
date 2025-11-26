import type {
  TraceListItem,
  TraceMetricBucket,
  TracePaginationResponse,
  TraceCursor,
  TraceFilters,
  TraceDetail,
  TraceSpan,
  SpanEvent,
  Attribute,
  SpanLink,
} from "./types";

/**
 * Generate mock trace metric buckets for the last 24 hours
 */
export function generateMockTraceMetricBuckets(): TraceMetricBucket[] {
  const buckets: TraceMetricBucket[] = [];
  const now = new Date();
  const bucketsCount = 48;

  for (let i = bucketsCount - 1; i >= 0; i--) {
    const bucketStart = new Date(now.getTime() - i * 30 * 60 * 1000);
    const hour = bucketStart.getHours();

    const isBusinessHours = hour >= 9 && hour <= 17;
    const baseTraffic = isBusinessHours ? 800 : 200;
    const variance = Math.random() * 0.3 - 0.15;
    const traceCount = Math.floor(baseTraffic * (1 + variance));

    const baseLatency = isBusinessHours ? 150 : 80;
    const latencyVariance = Math.random() * 0.4 - 0.2;
    const avgDuration = baseLatency * (1 + latencyVariance);

    const hasErrorSpike = Math.random() < 0.05;
    const baseErrorRate = 0.02;
    const errorRate = hasErrorSpike
      ? 0.15
      : baseErrorRate + Math.random() * 0.02;

    buckets.push({
      bucket_start: bucketStart.toISOString(),
      trace_count: traceCount,
      avg_duration_ms: avgDuration,
      p50_duration_ms: avgDuration * 0.7,
      p95_duration_ms: avgDuration * 2.5,
      p99_duration_ms: avgDuration * 4.0,
      error_rate: errorRate,
    });
  }

  return buckets;
}

/**
 * Seeded random number generator for deterministic data
 */
class SeededRandom {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed;
  }

  next(): number {
    // Linear congruential generator
    this.seed = (this.seed * 1664525 + 1013904223) % 2 ** 32;
    return this.seed / 2 ** 32;
  }

  nextInt(max: number): number {
    return Math.floor(this.next() * max);
  }
}

/**
 * Generate a deterministic span ID from a seed
 */
function generateSpanId(seed: number): string {
  const chars = "0123456789abcdef";
  const rng = new SeededRandom(seed);
  let spanId = "";
  for (let i = 0; i < 16; i++) {
    spanId += chars[rng.nextInt(16)];
  }
  return spanId;
}

/**
 * Generate a deterministic trace ID from a seed
 */
function generateTraceId(seed: number): string {
  const chars = "0123456789abcdef";
  const rng = new SeededRandom(seed);
  let traceId = "";
  for (let i = 0; i < 32; i++) {
    traceId += chars[rng.nextInt(16)];
  }
  return traceId;
}

/**
 * In-memory "database" of traces - generated once and cached
 * This simulates a real database with stable, queryable data
 */
class TraceDatabase {
  private traces: TraceListItem[] = [];
  private readonly TOTAL_TRACES = 10000; // Large dataset for realistic scrolling
  private initialized = false;

  /**
   * Initialize the database with deterministic data
   */
  private initialize(): void {
    if (this.initialized) return;

    const services = [
      "api-gateway",
      "auth-service",
      "data-processor",
      "ml-inference",
      "notification-service",
    ];
    const operations = [
      "GET /users/:id",
      "POST /auth/login",
      "POST /data/process",
      "POST /ml/predict",
      "POST /notifications/send",
      "GET /health",
      "POST /batch/process",
      "GET /metrics",
    ];
    const spaces = ["production", "staging"];
    const names = ["api-service", "ml-pipeline", "data-ingestion"];
    const versions = ["v1.2.3", "v1.2.4", "v1.3.0"];

    const now = new Date();

    // Generate traces going back 7 days with consistent spacing
    for (let i = 0; i < this.TOTAL_TRACES; i++) {
      const rng = new SeededRandom(i);

      // Space traces consistently (every ~1 minute on average over 7 days)
      const minutesBack = (i * 7 * 24 * 60) / this.TOTAL_TRACES;
      const createdAt = new Date(now.getTime() - minutesBack * 60 * 1000);

      const serviceName = services[rng.nextInt(services.length)];
      const rootOperation = operations[rng.nextInt(operations.length)];

      const hasErrors = rng.next() < 0.05;
      const statusCode = hasErrors
        ? [500, 502, 503, 504][rng.nextInt(4)]
        : [200, 201, 204][rng.nextInt(3)];

      const baseDuration = rootOperation.includes("batch")
        ? 5000
        : rootOperation.includes("ml")
        ? 800
        : rootOperation.includes("GET")
        ? 50
        : 200;
      const durationMs = Math.floor(baseDuration * (0.5 + rng.next() * 1.5));

      const startTime = new Date(createdAt.getTime() - durationMs);
      const endTime = createdAt;

      const spanCount = Math.floor(3 + durationMs / 100 + rng.next() * 5);

      this.traces.push({
        trace_id: generateTraceId(i),
        space: spaces[rng.nextInt(spaces.length)],
        name: names[rng.nextInt(names.length)],
        version: versions[rng.nextInt(versions.length)],
        scope: "default",
        service_name: serviceName,
        root_operation: rootOperation,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        duration_ms: durationMs,
        status_code: statusCode,
        status_message: hasErrors ? getErrorMessage(statusCode) : null,
        span_count: spanCount,
        has_errors: hasErrors,
        error_count: hasErrors ? Math.floor(rng.next() * 3) + 1 : 0,
        created_at: createdAt.toISOString(),
      });
    }

    // Sort by created_at descending (newest first) - this is our "database index"
    this.traces.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    this.initialized = true;
    console.log(
      `📊 Mock database initialized with ${this.TOTAL_TRACES} traces`
    );
  }

  /**
   * Query traces with cursor-based pagination (simulates database query)
   */
  query(
    limit: number,
    cursor?: TraceCursor,
    direction?: "next" | "previous"
  ): TracePaginationResponse {
    this.initialize();

    let startIndex = 0;

    if (cursor) {
      // Find the cursor position in our "database"
      const cursorIndex = this.traces.findIndex(
        (t) =>
          t.trace_id === cursor.trace_id && t.created_at === cursor.created_at
      );

      if (cursorIndex === -1) {
        console.warn("Cursor not found, starting from beginning");
        startIndex = 0;
      } else {
        if (direction === "next") {
          // Get older traces (move forward in array since sorted newest-first)
          startIndex = cursorIndex + 1;
        } else if (direction === "previous") {
          // Get newer traces (move backward in array)
          startIndex = Math.max(0, cursorIndex - limit);
        }
      }
    }

    // Extract the page of results
    const items = this.traces.slice(startIndex, startIndex + limit);

    // Determine if there are more pages
    const hasNext = startIndex + limit < this.traces.length;
    const hasPrevious = startIndex > 0;

    // Create cursors
    let nextCursor: TraceCursor | undefined;
    let previousCursor: TraceCursor | undefined;

    if (items.length > 0) {
      const lastItem = items[items.length - 1];
      nextCursor = {
        created_at: lastItem.created_at,
        trace_id: lastItem.trace_id,
      };

      const firstItem = items[0];
      previousCursor = {
        created_at: firstItem.created_at,
        trace_id: firstItem.trace_id,
      };
    }

    return {
      items,
      has_next: hasNext,
      has_previous: hasPrevious,
      next_cursor: hasNext ? nextCursor : undefined,
      previous_cursor: hasPrevious ? previousCursor : undefined,
    };
  }

  /**
   * Get total count (simulates COUNT query)
   */
  getTotalCount(): number {
    this.initialize();
    return this.traces.length;
  }
}

// Singleton instance of our mock database
const traceDB = new TraceDatabase();

function getErrorMessage(statusCode: number): string {
  const messages: Record<number, string> = {
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
  };
  return messages[statusCode] || "Unknown Error";
}

/**
 * Generate mock pagination response using the in-memory database
 */
export function generateMockTracePaginationResponse(
  limit: number = 25,
  cursor?: TraceCursor,
  direction?: "next" | "previous"
): TracePaginationResponse {
  return traceDB.query(limit, cursor, direction);
}

/**
 * Mock async fetch for trace pagination data
 * Now queries a stable, deterministic dataset
 */
export async function fetchTraces(
  filters: TraceFilters & {
    cursor_created_at?: string;
    cursor_trace_id?: string;
    direction?: "next" | "previous";
  }
): Promise<TracePaginationResponse> {
  // Simulate network latency
  await new Promise((resolve) =>
    setTimeout(resolve, 100 + Math.random() * 400)
  );

  let cursor: TraceCursor | undefined;
  if (filters.cursor_created_at && filters.cursor_trace_id) {
    cursor = {
      created_at: filters.cursor_created_at,
      trace_id: filters.cursor_trace_id,
    };
  }

  return generateMockTracePaginationResponse(
    filters.limit || 25,
    cursor,
    filters.direction
  );
}

/**
 * Get total trace count for debugging/testing
 */
export function getMockTraceCount(): number {
  return traceDB.getTotalCount();
}

/**
 * Generate mock spans for a trace matching backend structure
 */
function generateSpansForTrace(
  trace: TraceListItem,
  seed: number
): TraceSpan[] {
  const rng = new SeededRandom(seed);
  const spans: TraceSpan[] = [];
  const spanCount = trace.span_count || 5;

  const operations = [
    { name: "http.request", kind: "SPAN_KIND_SERVER", service: "api-gateway" },
    { name: "db.query", kind: "SPAN_KIND_CLIENT", service: "database" },
    { name: "cache.get", kind: "SPAN_KIND_CLIENT", service: "cache" },
    {
      name: "http.client.request",
      kind: "SPAN_KIND_CLIENT",
      service: "downstream-api",
    },
    {
      name: "queue.publish",
      kind: "SPAN_KIND_PRODUCER",
      service: "message-queue",
    },
    {
      name: "process.execute",
      kind: "SPAN_KIND_INTERNAL",
      service: "api-gateway",
    },
    {
      name: "auth.validate",
      kind: "SPAN_KIND_INTERNAL",
      service: "auth-service",
    },
  ];

  const traceStartTime = new Date(trace.start_time).getTime();
  const traceDuration = trace.duration_ms || 1000;
  const traceEndTime = traceStartTime + traceDuration;
  const rootSpanId = generateSpanId(seed);

  // Create root span (spans the entire trace duration)
  const rootSpan: TraceSpan = {
    trace_id: trace.trace_id,
    span_id: rootSpanId,
    parent_span_id: null,
    span_name: trace.root_operation || "GET /api/endpoint",
    span_kind: "SPAN_KIND_SERVER",
    start_time: trace.start_time,
    end_time: trace.end_time || new Date(traceEndTime).toISOString(),
    duration_ms: traceDuration,
    status_code: trace.has_errors ? 2 : 1,
    status_message: trace.status_message,
    attributes: [
      { key: "service.name", value: trace.service_name || "api-gateway" },
      { key: "http.method", value: trace.scope || "GET" },
      { key: "http.url", value: trace.root_operation || "/api/endpoint" },
      { key: "http.status_code", value: trace.status_code },
      { key: "component", value: "http" },
    ],
    events: trace.has_errors
      ? [
          {
            timestamp: new Date(
              traceStartTime + traceDuration * 0.9
            ).toISOString(),
            name: "exception",
            attributes: [
              { key: "exception.type", value: "InternalServerError" },
              {
                key: "exception.message",
                value: trace.status_message || "Internal error occurred",
              },
              {
                key: "exception.stacktrace",
                value:
                  "Error: Internal error\n  at handler (/app/handler.js:45:10)",
              },
            ],
            dropped_attributes_count: 0,
          },
        ]
      : [],
    links: [],
    depth: 0,
    path: [rootSpanId],
    root_span_id: rootSpanId,
    span_order: 0,
    input: JSON.stringify({
      method: trace.scope || "GET",
      url: trace.root_operation || "/api/endpoint",
      headers: {
        "content-type": "application/json",
        "user-agent": "opsml-client/1.0",
      },
      body: trace.scope === "POST" ? { data: "sample input" } : null,
    }),
    output: JSON.stringify({
      status: trace.status_code,
      body: trace.has_errors
        ? { error: trace.status_message }
        : { result: "success", data: {} },
      duration_ms: traceDuration,
    }),
  };

  spans.push(rootSpan);

  // Generate child spans with realistic timing
  let currentTime = traceStartTime;
  let parentStack: TraceSpan[] = [rootSpan];
  let currentOrder = 1;

  for (let i = 1; i < spanCount; i++) {
    const operation = operations[rng.nextInt(operations.length)];

    // Decide whether to create a child or sibling span
    const isChild = rng.next() > 0.3 && parentStack.length < 4;

    if (!isChild && parentStack.length > 1) {
      // Move up to parent level (create sibling)
      parentStack.pop();
    }

    const currentParent = parentStack[parentStack.length - 1];
    const parentEndTime = new Date(currentParent.end_time!).getTime();

    // Calculate available time window for this span
    // Spans must fit within their parent's time window
    const maxEndTime = parentEndTime;
    const availableTime = maxEndTime - currentTime;

    if (availableTime <= 1) {
      // Not enough time left in parent span, skip to next iteration
      continue;
    }

    // Calculate span duration based on operation type
    let baseDuration: number;
    if (operation.name.includes("db")) {
      baseDuration = 20 + rng.next() * 50; // 20-70ms
    } else if (operation.name.includes("cache")) {
      baseDuration = 5 + rng.next() * 15; // 5-20ms
    } else if (operation.name.includes("http")) {
      baseDuration = 50 + rng.next() * 200; // 50-250ms
    } else if (operation.name.includes("queue")) {
      baseDuration = 10 + rng.next() * 30; // 10-40ms
    } else {
      baseDuration = 15 + rng.next() * 50; // 15-65ms (internal)
    }

    // Ensure span doesn't exceed available time
    const spanDuration = Math.min(
      Math.floor(baseDuration),
      Math.floor(availableTime * 0.9) // Leave some buffer
    );

    if (spanDuration <= 0) {
      continue;
    }

    const spanStartTime = currentTime;
    const spanEndTime = spanStartTime + spanDuration;

    // Determine if this span has an error
    const hasError = trace.has_errors && rng.next() < 0.3;
    const statusCode = hasError ? 2 : 1;

    const spanId = generateSpanId(seed + i);
    const serviceName = operation.service;
    const spanPath = [...currentParent.path, spanId];

    // Create attributes based on operation type
    const attributes: Attribute[] = [
      { key: "service.name", value: serviceName },
      { key: "component", value: operation.name.split(".")[0] },
    ];

    if (operation.name.includes("http")) {
      attributes.push(
        { key: "http.method", value: "GET" },
        { key: "http.url", value: `/api/${serviceName}` },
        { key: "http.status_code", value: hasError ? 500 : 200 },
        { key: "peer.service", value: serviceName }
      );
    } else if (operation.name.includes("db")) {
      attributes.push(
        { key: "db.system", value: "postgresql" },
        { key: "db.statement", value: "SELECT * FROM users WHERE id = $1" },
        { key: "db.name", value: "production" },
        { key: "peer.service", value: "postgres" }
      );
    } else if (operation.name.includes("cache")) {
      attributes.push(
        { key: "cache.system", value: "redis" },
        { key: "cache.key", value: `user:${i}:profile` },
        { key: "peer.service", value: "redis" }
      );
    } else if (operation.name.includes("queue")) {
      attributes.push(
        { key: "messaging.system", value: "rabbitmq" },
        { key: "messaging.destination", value: "task_queue" },
        { key: "peer.service", value: "rabbitmq" }
      );
    }

    // Generate events for errors
    const events: SpanEvent[] = hasError
      ? [
          {
            timestamp: new Date(
              spanStartTime + spanDuration * 0.8
            ).toISOString(),
            name: "exception",
            attributes: [
              {
                key: "exception.type",
                value: operation.name.includes("db")
                  ? "DatabaseError"
                  : "ServiceError",
              },
              {
                key: "exception.message",
                value: operation.name.includes("db")
                  ? "Connection timeout"
                  : "Service unavailable",
              },
              {
                key: "exception.stacktrace",
                value: `Error: ${operation.name} failed\n  at ${serviceName}.execute()`,
              },
            ],
            dropped_attributes_count: 0,
          },
        ]
      : [];

    // Occasionally add span links (5% chance)
    const links: SpanLink[] =
      rng.next() < 0.05
        ? [
            {
              trace_id: generateTraceId(seed + i + 1000),
              span_id: generateSpanId(seed + i + 2000),
              trace_state: "",
              attributes: [{ key: "link.type", value: "follows_from" }],
              dropped_attributes_count: 0,
            },
          ]
        : [];

    const span: TraceSpan = {
      trace_id: trace.trace_id,
      span_id: spanId,
      parent_span_id: currentParent.span_id,
      span_name: operation.name,
      span_kind: operation.kind,
      start_time: new Date(spanStartTime).toISOString(),
      end_time: new Date(spanEndTime).toISOString(),
      duration_ms: spanDuration,
      status_code: statusCode,
      status_message: hasError ? "Internal error occurred" : null,
      attributes,
      events,
      links,
      depth: currentParent.depth + 1,
      path: spanPath,
      root_span_id: rootSpanId,
      span_order: currentOrder++,
      input: operation.name.includes("db")
        ? JSON.stringify({
            query: "SELECT * FROM users WHERE id = $1",
            params: [123],
          })
        : operation.name.includes("http")
        ? JSON.stringify({ method: "GET", url: `/api/${serviceName}` })
        : operation.name.includes("cache")
        ? JSON.stringify({ operation: "GET", key: `user:${i}:profile` })
        : null,
      output: hasError
        ? JSON.stringify({ error: "Internal error", status: 500 })
        : operation.name.includes("db")
        ? JSON.stringify({ rows: 1, result: [{ id: 123, name: "user" }] })
        : operation.name.includes("cache")
        ? JSON.stringify({ hit: true, value: { cached: "data" } })
        : JSON.stringify({ status: 200, data: {} }),
    };

    spans.push(span);

    if (isChild) {
      // Add to parent stack for nested spans
      parentStack.push(span);
      // Child spans continue from same time point (parallel/nested execution)
    } else {
      // Sibling spans continue after this span ends (sequential execution)
      currentTime = spanEndTime;
    }
  }

  return spans;
}

/**
 * Generate a full trace detail with spans
 */
export function generateTraceDetail(trace: TraceListItem): TraceDetail {
  const seed = parseInt(trace.trace_id.substring(0, 8), 16);
  const spans = generateSpansForTrace(trace, seed);

  const serviceSet = new Set(
    spans
      .map((s) => s.attributes.find((a) => a.key === "service.name")?.value)
      .filter(Boolean)
  );
  const errorSpans = spans.filter((s) => s.status_code === 2);

  return {
    trace_id: trace.trace_id,
    spans,
    root_span: spans[0],
    total_duration_ms: trace.duration_ms || 0,
    service_count: serviceSet.size,
    span_count: spans.length,
    error_count: errorSpans.length,
    critical_path_duration_ms: trace.duration_ms || 0,
  };
}

/**
 * Mock async fetch for trace detail
 */
export async function fetchTraceDetail(
  traceId: string
): Promise<TraceDetail | null> {
  // Simulate network latency
  await new Promise((resolve) =>
    setTimeout(resolve, 200 + Math.random() * 300)
  );

  // Find the trace in our database
  const trace = traceDB
    .query(10000, undefined, undefined)
    .items.find((t) => t.trace_id === traceId);

  if (!trace) {
    return null;
  }

  return generateTraceDetail(trace);
}

export const mockTraceMetrics = generateMockTraceMetricBuckets();
export const mockTracePaginationResponse =
  generateMockTracePaginationResponse(25);
