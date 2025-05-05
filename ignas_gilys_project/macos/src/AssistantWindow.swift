import AppKit

class AssistantWindow: NSPanel {
    var isLoading: Bool = false {
        didSet {
            if isLoading {
                progressIndicator.startAnimation(nil)
                progressIndicator.isHidden = false
            } else {
                progressIndicator.stopAnimation(false)
                progressIndicator.isHidden = true
            }
        }
    }

    var text: String = "" {
        didSet {
            textView.stringValue = text
            textView.isHidden = text.isEmpty
            separator.isHidden = textView.isHidden
            
            updateWindowSize()
        }
    }

    let textField = NSTextField()
    let progressIndicator = NSProgressIndicator()
    let separator = NSBox()
    let textView = NSTextField()

    var prompt: String {
        textField.stringValue
    }
    var sendButtonClicked: () -> Void = {}

    init() {
        super.init(
            contentRect: .zero,
            styleMask: [.titled, .closable, .fullSizeContentView, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )

        isFloatingPanel = true
        level = .floating

        collectionBehavior.insert(.fullScreenAuxiliary)

        titleVisibility = .hidden
        titlebarAppearsTransparent = true

        isMovableByWindowBackground = true
        isReleasedWhenClosed = false
        hidesOnDeactivate = false

        standardWindowButton(.closeButton)?.isHidden = true
        standardWindowButton(.miniaturizeButton)?.isHidden = true
        standardWindowButton(.zoomButton)?.isHidden = true

        let rootView = NSView()

        textField.translatesAutoresizingMaskIntoConstraints = false
        textField.isBezeled = false
        textField.drawsBackground = false
        textField.usesSingleLineMode = true
        textField.focusRingType = .none
        textField.font = .systemFont(ofSize: 13)
        textField.target = self
        textField.action = #selector(sendButtonAction)

        let button = NSButton(title: "Send", target: self, action: #selector(sendButtonAction))
        button.translatesAutoresizingMaskIntoConstraints = false

        let textFieldContainer = NSView()
        textFieldContainer.translatesAutoresizingMaskIntoConstraints = false

        textFieldContainer.addSubview(textField)
        textFieldContainer.addSubview(button)

        NSLayoutConstraint.activate([
            textField.topAnchor.constraint(equalTo: textFieldContainer.topAnchor),
            textField.leadingAnchor.constraint(equalTo: textFieldContainer.leadingAnchor),
            textField.bottomAnchor.constraint(equalTo: textFieldContainer.bottomAnchor),
            textField.trailingAnchor.constraint(equalTo: button.leadingAnchor, constant: -8),
            button.topAnchor.constraint(equalTo: textFieldContainer.topAnchor),
            button.trailingAnchor.constraint(equalTo: textFieldContainer.trailingAnchor),
            button.bottomAnchor.constraint(equalTo: textFieldContainer.bottomAnchor),
        ])

        progressIndicator.translatesAutoresizingMaskIntoConstraints = false
        progressIndicator.style = .bar
        progressIndicator.isIndeterminate = true
        progressIndicator.isHidden = true

        separator.translatesAutoresizingMaskIntoConstraints = false
        separator.boxType = .separator
        separator.isHidden = true

        textView.translatesAutoresizingMaskIntoConstraints = false
        textView.isBezeled = false
        textView.drawsBackground = false
        textView.focusRingType = .none
        textView.isEditable = false
        textView.isSelectable = true
        textView.font = NSFont(name: "SF Mono", size: 13)
        textView.usesSingleLineMode = false
        textView.cell?.wraps = true
        textView.cell?.lineBreakMode = .byWordWrapping
        textView.preferredMaxLayoutWidth = 560
        textView.isHidden = true

        let stackView = NSStackView(views: [
            textFieldContainer,
            progressIndicator,
            separator,
            textView,
        ])
        stackView.orientation = .vertical
        stackView.alignment = .leading
        stackView.spacing = 8

        rootView.addSubview(stackView)

        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: rootView.topAnchor, constant: 20),
            stackView.leadingAnchor.constraint(equalTo: rootView.leadingAnchor, constant: 20),
            stackView.trailingAnchor.constraint(equalTo: rootView.trailingAnchor, constant: -20),
            stackView.bottomAnchor.constraint(equalTo: rootView.bottomAnchor, constant: -20),
            
            textView.widthAnchor.constraint(equalTo: stackView.widthAnchor)
        ])

        contentView = rootView

        reset()
    }

    override var canBecomeKey: Bool {
        return true
    }

    override var canBecomeMain: Bool {
        return true
    }

    override func close() {
        reset()
        super.close()
    }

    private func reset() {
        isLoading = false
        textField.stringValue = ""
        text = ""
        updateWindowSize()
    }

    private func updateWindowSize() {
        let maxWidth: CGFloat = 600
        let padding: CGFloat = 40
        
        let textFieldHeight: CGFloat = 22
        let progressIndicatorHeight: CGFloat = isLoading ? 20 : 0
        let separatorHeight: CGFloat = text.isEmpty ? 0 : 1
        
        var textHeight: CGFloat = 0
        if !text.isEmpty {
            let textWidth = maxWidth - padding
            let size = textView.sizeThatFits(CGSize(width: textWidth, height: .greatestFiniteMagnitude))
            textHeight = size.height
        }
        
        let spacing: CGFloat = 8
        let totalHeight = 40 +
            textFieldHeight +
            (isLoading ? spacing + progressIndicatorHeight : 0) +
            (text.isEmpty ? 0 : spacing + separatorHeight) +
            (text.isEmpty ? 0 : spacing + textHeight)
        
        setContentSize(CGSize(width: maxWidth, height: totalHeight))
        minSize = CGSize(width: maxWidth, height: textFieldHeight + 40)
        maxSize = CGSize(width: maxWidth, height: 1200)
    }

    @objc
    private func sendButtonAction() {
        sendButtonClicked()
    }
}
