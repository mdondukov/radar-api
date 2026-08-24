#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="${1:-radar-api:dev}"

echo "Building $IMAGE_NAME..."
echo "Context: $PROJECT_DIR"

docker build \
  -f "$PROJECT_DIR/deploy/docker/Dockerfile" \
  -t "$IMAGE_NAME" \
  "$PROJECT_DIR"

echo "Done: $IMAGE_NAME"
