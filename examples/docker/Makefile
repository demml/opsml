SHELL:=/bin/bash
PROJECT=docker

docker.up:
	docker-compose up --build webserver
docker.down:
	docker-compose down
docker.clean:
	docker.down
	-docker rmi $$(docker images -a | grep ${PROJECT} | tr -s ' ' | cut -d' ' -f3)
	-docker image prune -f
docker.run:
	docker-compose run opsml-api-service
