import Cocoa
import Carbon
import os

@main
class Main: NSObject, NSApplicationDelegate {
    private let logger = Logger(subsystem: "com.assistant", category: "General")
  
    lazy var statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    lazy var assistantWindow = AssistantWindow()
    
    private var selectedText = ""
    private var shiftPressCount = 0
    private var lastShiftPressTime: TimeInterval = 0
    private let doublePressThreshold: TimeInterval = 0.3
    private var resetTimer: Timer?

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        setupStatusItem()
        
        assistantWindow.sendButtonClicked = {
            self.assistantWindow.isLoading = true
            
            let command = """
                \(self.selectedText)
                \(self.assistantWindow.prompt)
                """
            
            sendAIRequest(command: command) { (result) in
                DispatchQueue.main.async {
                    self.assistantWindow.isLoading = false
                    self.assistantWindow.text = result ?? ""
                }
            }
        }
        
        let trustedCheckOptionPrompt = kAXTrustedCheckOptionPrompt.takeRetainedValue() as NSString
        let options = [trustedCheckOptionPrompt: true] as CFDictionary
        if AXIsProcessTrustedWithOptions(options) {
            setup()
        } else {
            waitPermisionGranted {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                    self.setup()
                }
            }
        }
    }

    private func setupStatusItem() {
        if let button = statusItem.button {
            button.title = "🧠"
        }

        let menu = NSMenu()

        let openItem = NSMenuItem(title: "Open Assistant", action: #selector(openAssistantWindow), keyEquivalent: "")
        openItem.target = self
        menu.addItem(openItem)
        
        let apiKeyItem = NSMenuItem(title: "Set API Key", action: #selector(handleSetAPIKey), keyEquivalent: "k")
        apiKeyItem.target = self
        menu.addItem(apiKeyItem)
        
        let modelItem = NSMenuItem(title: "Set Model", action: #selector(handleSetModel), keyEquivalent: "m")
        modelItem.target = self
        menu.addItem(modelItem)

        let systemRoleItem = NSMenuItem(title: "Set System Role", action: #selector(handleSetSystemRole), keyEquivalent: "r")
        systemRoleItem.target = self
        menu.addItem(systemRoleItem)

        menu.addItem(NSMenuItem.separator())

        let quitItem = NSMenuItem(title: "Quit", action: #selector(quitApp), keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)

        statusItem.menu = menu
    }

    @objc private func handleSetAPIKey() {
        let alert = NSAlert()
        alert.messageText = "Enter OpenAI API Key"
        alert.informativeText = "Your key will be stored securely in the Keychain"
        
        let textField = NSSecureTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24))
        textField.placeholderString = "sk-..."
        alert.accessoryView = textField
        alert.addButton(withTitle: "Save")
        alert.addButton(withTitle: "Cancel")
        
        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let apiKey = textField.stringValue
            saveAPIKey(apiKey)
        }
    }

    @objc private func openAssistantWindow() {
        processSelectedText()
        showAssistantWindowAtCursor()
    }

    @objc private func quitApp() {
        NSApp.terminate(nil)
    }

    private func setup() {
        NSEvent.addLocalMonitorForEvents(matching: .flagsChanged) { event in
            self.handleFlagsChanged(event)
            return event
        }
        
        NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged) { event in
            self.handleFlagsChanged(event)
        }
        
        NotificationCenter.default.addObserver(self, selector: #selector(closeFloatingPanel),
            name: NSWindow.didResignKeyNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(closeFloatingPanel),
            name: NSWindow.didResignMainNotification, object: nil)
    }
    
    private func handleFlagsChanged(_ event: NSEvent) {
        guard event.type == .flagsChanged else { return }
        
        let currentTime = Date().timeIntervalSince1970
        let isShiftPressed = event.modifierFlags.contains(.shift)
        
        if isShiftPressed {
            resetTimer?.invalidate()
            
            if (currentTime - lastShiftPressTime) < doublePressThreshold {
                shiftPressCount += 1
            } else {
                shiftPressCount = 1
            }
            
            lastShiftPressTime = currentTime
            
            if shiftPressCount >= 2 {
                shiftPressCount = 0
                resetTimer?.invalidate()
                DispatchQueue.main.async {
                    self.processSelectedText()
                    self.showAssistantWindowAtCursor()
                }
            } else {
                resetTimer = Timer.scheduledTimer(withTimeInterval: doublePressThreshold, repeats: false) { _ in
                    self.shiftPressCount = 0
                }
            }
        }
    }
    
    private func processSelectedText() {
        self.selectedText = ""
        let systemWideElement = AXUIElementCreateSystemWide()
        var focusedElement: AnyObject?
        
        let focusedElementError = AXUIElementCopyAttributeValue(
            systemWideElement,
            kAXFocusedUIElementAttribute as CFString,
            &focusedElement
        )
        
        guard let focusedElement = focusedElement, focusedElementError == .success else {
            if let clipboardText = NSPasteboard.general.string(forType: .string) {
                self.selectedText = clipboardText
            }
            return
        }
        
        var selectedTextValue: AnyObject?
        let selectedTextValueError = AXUIElementCopyAttributeValue(
            focusedElement as! AXUIElement,
            kAXSelectedTextAttribute as CFString,
            &selectedTextValue
        )
        
        if let selectedTextValue = selectedTextValue, selectedTextValueError == .success {
            self.selectedText = "\(selectedTextValue)"
        } else {
            var selectedTextMarkerRangeValue: AnyObject?
            let selectedTextMarkerRangeValueError = AXUIElementCopyAttributeValue(
                focusedElement as! AXUIElement,
                "AXSelectedTextMarkerRange" as CFString,
                &selectedTextMarkerRangeValue
            )
            
            guard let selectedTextMarkerRangeValue = selectedTextMarkerRangeValue,
                  selectedTextMarkerRangeValueError == .success else {
                return
            }
            
            var stringForTextMarkerRangeValue: AnyObject?
            let stringForTextMarkerRangeValueError = AXUIElementCopyParameterizedAttributeValue(
                focusedElement as! AXUIElement,
                "AXStringForTextMarkerRange" as CFString,
                selectedTextMarkerRangeValue,
                &stringForTextMarkerRangeValue
            )
            
            guard let stringForTextMarkerRangeValue = stringForTextMarkerRangeValue,
                  stringForTextMarkerRangeValueError == .success else {
                return
            }
            
            self.selectedText = "\(stringForTextMarkerRangeValue)"
        }
    }
    
    private func showAssistantWindowAtCursor() {
        let mouseLocation = NSEvent.mouseLocation
        var windowOrigin = mouseLocation
        let windowSize = assistantWindow.frame.size
        
        guard let screen = NSScreen.main else { return }
        let screenFrame = screen.visibleFrame
        let verticalPadding: CGFloat = 20
        
        windowOrigin.x += verticalPadding

        let spaceBelow = screenFrame.maxY - mouseLocation.y

        if spaceBelow > windowSize.height + verticalPadding {
            windowOrigin.y -= windowSize.height + verticalPadding
        } else {
            windowOrigin.y += verticalPadding
        }

        if windowOrigin.x + windowSize.width > screenFrame.maxX {
            windowOrigin.x = screenFrame.maxX - windowSize.width
        }
        if windowOrigin.x < screenFrame.minX {
            windowOrigin.x = screenFrame.minX
        }

        if windowOrigin.y + windowSize.height > screenFrame.maxY {
            windowOrigin.y = screenFrame.maxY - windowSize.height
        }
        if windowOrigin.y < screenFrame.minY {
            windowOrigin.y = screenFrame.minY
        }
        
        assistantWindow.text = self.selectedText
        assistantWindow.setFrameOrigin(windowOrigin)
        assistantWindow.orderFront(nil)
        assistantWindow.makeKey()
        NSApp.activate(ignoringOtherApps: true)
    }
    
    private func waitPermisionGranted(completion: @escaping () -> Void) {
        logger.info("Waiting for permissions")
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            if AXIsProcessTrusted() {
                completion()
            } else {
                self.waitPermisionGranted(completion: completion)
            }
        }
    }
    
    @objc func closeFloatingPanel() {
        assistantWindow.close()
    }
    
    private func saveAPIKey(_ key: String) {
        let service = "com.assistant.apiKey"
        let account = "defaultUser"
        
        guard let data = key.data(using: .utf8) else { return }
        
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: account,
            kSecValueData: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    @objc private func handleSetModel() {
        let alert = NSAlert()
        alert.messageText = "Set Model"
        alert.informativeText = "Enter the model name (e.g., gpt-3.5-turbo, gpt-4)"
        
        let textField = NSTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24))
        textField.stringValue = UserDefaults.standard.string(forKey: "selectedModel") ?? "gpt-3.5-turbo"
        alert.accessoryView = textField
        alert.addButton(withTitle: "Save")
        alert.addButton(withTitle: "Cancel")
        
        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let model = textField.stringValue
            UserDefaults.standard.set(model, forKey: "selectedModel")
        }
    }

    @objc private func handleSetSystemRole() {
        let alert = NSAlert()
        alert.messageText = "Set System Role"
        alert.informativeText = "Enter the system role message"
        
        let scrollView = NSScrollView(frame: NSRect(x: 0, y: 0, width: 300, height: 100))
        let textView = NSTextView(frame: scrollView.bounds)
        textView.string = UserDefaults.standard.string(forKey: "systemRole") ?? "You are a helpful assistant."
        scrollView.documentView = textView
        alert.accessoryView = scrollView
        alert.addButton(withTitle: "Save")
        alert.addButton(withTitle: "Cancel")
        
        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let role = textView.string
            UserDefaults.standard.set(role, forKey: "systemRole")
        }
    }
}
