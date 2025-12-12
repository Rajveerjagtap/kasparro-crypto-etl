#!/bin/bash
set -e

IMAGE_NAME="assignment_kasparro_new-backend"

echo "=== Building Docker Image ==="
echo "Building fresh image to ensure all latest changes are included..."
docker compose build backend

echo "=== Push to Docker Hub ==="
echo "Please enter your Docker Hub username:"
read DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo "Username cannot be empty."
    exit 1
fi

echo "Logging in to Docker Hub..."
docker login

TARGET_IMAGE="$DOCKER_USERNAME/kasparro-backend:latest"

echo "Tagging image as $TARGET_IMAGE..."
docker tag $IMAGE_NAME:latest $TARGET_IMAGE

echo "Pushing image to Docker Hub..."
docker push $TARGET_IMAGE

echo "✅ Successfully pushed to Docker Hub!"
echo "View your image at: https://hub.docker.com/r/$DOCKER_USERNAME/kasparro-backend"
