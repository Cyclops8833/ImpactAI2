#!/bin/bash
# Production build and serve script for frontend

# Install dependencies
echo "Installing Node.js dependencies..."
yarn install

# Build the React app
echo "Building React app for production..."
yarn build

# Install serve to serve static files
echo "Installing serve for static file hosting..."
yarn global add serve

# Start serving the built app
echo "Starting ImpactAI Frontend..."
serve -s build -p ${PORT:-3000}