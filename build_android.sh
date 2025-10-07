#!/bin/bash

# Build script for Android with Capacitor

echo "Building MediSync for Android..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Build the app
echo "Building web assets..."
npm run build

# Copy web assets to Android platform
echo "Copying web assets to Android platform..."
npx cap copy android

# Sync plugins
echo "Syncing plugins..."
npx cap sync android

# Open in Android Studio
echo "Opening project in Android Studio..."
npx cap open android

echo "Android build process completed. Project opened in Android Studio."
echo "You can now build and run the app on your Android device or emulator."