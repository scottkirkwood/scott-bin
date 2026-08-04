#!/bin/bash
set -e

DEST_DIR="${HOME}/.local/bin"
BINARY_NAME="forusers-redirect"

mkdir -p "${DEST_DIR}"

echo "Building ${BINARY_NAME}..."
go build -o "${DEST_DIR}/${BINARY_NAME}" main.go

echo "Successfully installed ${BINARY_NAME} to ${DEST_DIR}/${BINARY_NAME}"
