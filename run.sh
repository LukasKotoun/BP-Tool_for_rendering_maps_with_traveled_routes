#!/bin/bash

if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE up --build

BE_CONTAINER_ID=$($DOCKER_COMPOSE ps -q backend)

if [ $# -gt 0 ]; then
    docker exec -it "$BE_CONTAINER_ID" python /app/osm_filter_invalid_geoms.py "$@"
fi

echo "All services are now running"