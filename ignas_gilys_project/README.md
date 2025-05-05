# Assistant

🧠
*A lightweight macOS ChatGPT wrapper application.*

## Summary

Assistant is a simple macOS utility that makes it easier to access AI assistance while working. It allows users to select any text in any application, type a prompt suffix and quickly send it to ChatGPT by double-pressing the Shift key. The selected text appears in a floating window near the cursor, where users can add a prompt and receive a response without leaving their current app.

The tool is developed as a native Swift application using macOS Cocoa frameworks. It offers basic customization options, such as choosing an OpenAI model (e.g., gpt-3.5-turbo, gpt-4) and setting a system role to guide the AI’s tone or behavior. API keys are stored securely in the macOS Keychain, and settings are accessible from a menu bar icon.

Assistant supports both Apple Silicon and Intel Macs through a universal binary. It requires macOS 12.0 (Monterey) or later, an OpenAI API key, and Accessibility permissions to function properly.

Users can install it by building from source using a provided script or by downloading a pre-built binary. The first-time setup involves setting an API key and granting the required permissions.

Typical use cases include summarizing content, drafting quick responses, or getting contextual explanations — all without switching away from the current task. Assistant is designed to be lightweight, convenient, and unobtrusive, offering a straightforward way to bring AI assistance into everyday macOS use.

## Feature overview
- **Quick Activation**: Double-press Shift key to capture selected text  
![Features](https://i.imgur.com/MzJ3KGM.png)
- **Floating Window**: Appears near your cursor position  
- **Secure API Key Storage**: Keys are saved in macOS Keychain  
<p align="center">
  <img src="https://i.imgur.com/EvLeO2Y.png" width="300"/>
</p>

- **Customizable Settings**:  
  - Choose your preferred OpenAI model (gpt-3.5-turbo, gpt-4, etc.)  
  <p align="center">
    <img src="https://i.imgur.com/XWmGUTF.png" width="300"/>
  </p>

  - Set a custom system role for the AI  
  <p align="center">
    <img src="https://i.imgur.com/RrAQKOd.png" width="300"/>
  </p>

- **Menu Bar Control**: Access settings and functions from the status bar  
- **Universal Binary**: Supports both Intel (x86_64) and Apple Silicon (arm64) Macs  
## Requirements

- macOS 12.0 (Monterey) or later  
- OpenAI API key  
- Accessibility permissions (for text selection capture)  

## Installation

### Option 1: Build from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/0ever/assistant.git
   cd assistant/macos
   ```

2. Build for your architecture:

   **For ARM architectures (Apple Silicon M1/M2/M3/M4):**
   ```bash
   ./build.sh arm64
   ```

   **For Intel Macs:**
   ```bash
   ./build.sh x86_64
   ```

3. The built application will be in the `build` directory. Drag it to your Applications folder.

### Option 2: Download Pre-built Binary

[Download pre-built binaries for ARM and x86 via this link](https://filebin.net/o24lmucyxws6a3fx)

## First Run Setup

1. Launch Assistant — you'll see a brain icon (🧠) in your menu bar.  
2. Click the menu bar icon and select **"Set API Key"** to enter your OpenAI API key.  
3. Grant accessibility permissions when prompted (required for text selection).

## Usage

### Basic Usage

- Select any text in any application
- Double-press the Shift key  
- The selected text will appear in a floating window  
- If no text was selected or the selected text is inaccessible, clipboard content will be used
- Add your prompt/question in the text field  
- Click "Send" to get an AI response  

## Troubleshooting

### Common Issues

**Text selection not working:**
- Ensure Assistant has Accessibility permissions in *System Settings > Privacy & Security > Accessibility*  
- Restart the application after granting permissions  

**API errors:**
- Verify your API key is correct and has sufficient credits  
- Check the model name is valid (*menu bar > Set Model*)  

**Build issues:**
- Ensure you have Xcode command line tools installed:  
  ```bash
  xcode-select --install
  ```
- Check build logs in `logs/xcodebuild.log`