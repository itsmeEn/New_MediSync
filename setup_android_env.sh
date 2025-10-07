#!/bin/bash

# Set Android environment variables
export ANDROID_HOME=/Users/judeibardaloza/Library/Android/sdk
export ANDROID_SDK_ROOT=/Users/judeibardaloza/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin

# Add to your shell profile for permanent setup
echo "export ANDROID_HOME=/Users/judeibardaloza/Library/Android/sdk" >> ~/.zshrc
echo "export ANDROID_SDK_ROOT=/Users/judeibardaloza/Library/Android/sdk" >> ~/.zshrc
echo "export PATH=\$PATH:\$ANDROID_HOME/platform-tools" >> ~/.zshrc
echo "export PATH=\$PATH:\$ANDROID_HOME/tools" >> ~/.zshrc
echo "export PATH=\$PATH:\$ANDROID_HOME/tools/bin" >> ~/.zshrc

echo "Android environment variables set up!"
echo "Please restart your terminal or run: source ~/.zshrc"
