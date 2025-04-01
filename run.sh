#!/bin/bash

if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE build

if [ $# -gt 0 ]; then
    $DOCKER_COMPOSE up -d backend
    $DOCKER_COMPOSE exec backend python /app/osm_filter_invalid_geoms.py "$@"
    $DOCKER_COMPOSE down
fi

$DOCKER_COMPOSE up
