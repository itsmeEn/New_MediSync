#!/bin/bash

# Set Android environment variables
export ANDROID_HOME=/Users/judeibardaloza/Library/Android/sdk
# ANDROID_SDK_ROOT is deprecated, but some older tools might still use it.
export ANDROID_SDK_ROOT=/Users/judeibardaloza/Library/Android/sdk

# Add essential Android SDK command-line tools to the PATH.
# The order can be important. Prepending ensures they are found first.
export PATH=$ANDROID_HOME/platform-tools:$PATH
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$PATH
export PATH=$ANDROID_HOME/emulator:$PATH

echo "Android environment variables have been set for the current session."
echo "To make this permanent, add the following lines to your ~/.zshrc or ~/.bash_profile:"
echo ""
echo 'export ANDROID_HOME=/Users/judeibardaloza/Library/Android/sdk'
echo 'export ANDROID_SDK_ROOT=/Users/judeibardaloza/Library/Android/sdk'
echo 'export PATH=$ANDROID_HOME/platform-tools:$PATH'
echo 'export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$PATH'
echo 'export PATH=$ANDROID_HOME/emulator:$PATH'
echo ""
echo "After adding them, restart your terminal or run: source ~/.zshrc"
