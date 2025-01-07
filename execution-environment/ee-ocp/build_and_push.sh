#!/bin/bash

set -e

IMAGE_NAME="ee-ocp"
IMAGE_TAG="1.0"
REGISTRY="quay.io/jealopez"

echo "Construyendo la imagen con ansible-builder..."
ansible-builder build -t ${IMAGE_NAME}:latest

echo "Etiquetando la imagen..."
podman tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Subiendo la imagen al registro..."
podman push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Imagen construida y subida exitosamente."
echo "La imagen subida es: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
