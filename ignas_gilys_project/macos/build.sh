#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if [ $# -ne 1 ]; then
    echo "Usage: $0 <architecture> (arm64 or x86_64)"
    exit 1
fi

ARCH_ARGUMENT="$1"
if [[ "$ARCH_ARGUMENT" != "arm64" && "$ARCH_ARGUMENT" != "x86_64" ]]; then
    echo "Error: Invalid architecture. Must be 'arm64' or 'x86_64'."
    exit 1
fi

PROJECT_NAME="${SCRIPT_DIR}/assistant.xcodeproj"
SCHEME_NAME="assistant"
CONFIGURATION="Release"
BUILD_DIR="${SCRIPT_DIR}/build"
LOG_DIR="${SCRIPT_DIR}/logs"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

rm -rf "$LOG_DIR"
mkdir -p "$LOG_DIR"

LOG_FILE="${LOG_DIR}/xcodebuild.log"

xcodebuild -project "$PROJECT_NAME" \
           -scheme "$SCHEME_NAME" \
           -configuration "$CONFIGURATION" \
           -derivedDataPath "${BUILD_DIR}/DerivedData" \
           SYMROOT="$BUILD_DIR" \
           CONFIGURATION_BUILD_DIR="$BUILD_DIR" \
           ARCHS="$ARCH_ARGUMENT" \
           VALID_ARCHS="$ARCH_ARGUMENT" \
           ONLY_ACTIVE_ARCH=NO \
           > "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Build succeeded. Logs saved to $LOG_FILE"
else
    echo "Build failed. Logs saved to $LOG_FILE"
fi