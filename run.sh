#!/bin/bash

if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi



if [ $# -gt 0 ]; then
    $DOCKER_COMPOSE up -d --build backend

    BE_CONTAINER_ID=$($DOCKER_COMPOSE ps -q backend)

    docker exec -it "$BE_CONTAINER_ID" python /app/osm_filter_invalid_geoms.py "$@"
fi

$DOCKER_COMPOSE up --build
