#!/bin/bash

# Build script for iOS with Capacitor

echo "Building MediSync for iOS..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Build the app
echo "Building web assets..."
npm run build

# Copy web assets to iOS platform
echo "Copying web assets to iOS platform..."
npx cap copy ios

# Sync plugins
echo "Syncing plugins..."
npx cap sync ios

# Open in Xcode (using IDE approach instead of direct build)
echo "Opening project in Xcode..."
npx cap open ios

echo "iOS build process completed. Project opened in Xcode."
echo "IMPORTANT: You need to manually select a device/simulator in Xcode and click the build button."
echo "The automatic build failed because no destination device was found."