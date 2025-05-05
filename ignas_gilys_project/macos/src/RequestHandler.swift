import Foundation

func sendAIRequest(command: String, completion: @escaping (String?) -> Void) {
    guard let url = URL(string: "https://api.openai.com/v1/chat/completions") else {
        completion("Invalid URL")
        return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")

    guard let apiKey = getAPIKey(), !apiKey.isEmpty else {
        completion("Error: API key not set. Please set it from the menu.")
        return
    }
    
    request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
    
    let json: [String: Any] = [
        "model": UserDefaults.standard.string(forKey: "selectedModel") ?? "gpt-3.5-turbo",
        "messages": [
            ["role": "system", "content": UserDefaults.standard.string(forKey: "systemRole") ?? "You are a helpful assistant."],
            ["role": "user", "content": command]
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    ]

    guard let jsonData = try? JSONSerialization.data(withJSONObject: json, options: []) else {
        completion("JSON Serialization failed")
        return
    }

    request.httpBody = jsonData

    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion("Network error: \(error.localizedDescription)")
            return
        }

        guard let data = data else {
            completion("No response data")
            return
        }
        
        do {
            let jsonResponse = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]

            if let errorInfo = jsonResponse?["error"] as? [String: Any],
               let errorMessage = errorInfo["message"] as? String {
                completion("Error: \(errorMessage)")
                return
            }

            if let choices = jsonResponse?["choices"] as? [[String: Any]],
               let message = choices.first?["message"] as? [String: Any],
               let content = message["content"] as? String {
                completion(content)
            } else {
                completion("Unexpected response format")
            }
        } catch {
            completion("JSON parsing error: \(error.localizedDescription)")
        }
    }

    task.resume()
}


private func getAPIKey() -> String? {
    let service = "com.assistant.apiKey"
    let account = "defaultUser"
    
    let query: [CFString: Any] = [
        kSecClass: kSecClassGenericPassword,
        kSecAttrService: service,
        kSecAttrAccount: account,
        kSecReturnData: kCFBooleanTrue!,
        kSecMatchLimit: kSecMatchLimitOne
    ]
    
    var result: AnyObject?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    
    guard status == errSecSuccess,
          let data = result as? Data,
          let key = String(data: data, encoding: .utf8) else {
        return nil
    }
    
    return key
}
