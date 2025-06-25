#!/bin/bash
# Build script for frontend deployment

echo "Installing dependencies..."
yarn install

echo "Building React app..."
yarn build

echo "Frontend build complete!"
echo "Build files are in the 'build' directory"