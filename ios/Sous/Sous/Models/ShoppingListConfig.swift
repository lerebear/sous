import Foundation

struct ShoppingListConfig {
    /// Ordered categories, each with an ordered list of item names (lowercased).
    let categories: [(name: String, items: [String])]

    /// Parse a TOML config file with the expected format:
    ///
    ///     [dairy]
    ///     items = ["milk", "butter"]
    ///
    ///     [produce]
    ///     items = ["potatoes", "onions"]
    ///
    init(contentsOf url: URL) throws {
        let content = try String(contentsOf: url, encoding: .utf8)
        self.categories = Self.parse(content)
    }

    init(from content: String) {
        self.categories = Self.parse(content)
    }

    /// Returns the category name for a given item, or nil if uncategorized.
    func category(for itemName: String) -> String? {
        let normalized = itemName.lowercased()
        for category in categories {
            if category.items.contains(normalized) {
                return category.name
            }
        }
        return nil
    }

    /// Returns a sort key for ordering items according to the config.
    /// Items in earlier categories sort first; within a category, items
    /// are sorted alphabetically. Uncategorized items sort last, alphabetically.
    func sortKey(for itemName: String) -> (Int, String) {
        let normalized = itemName.lowercased()
        for (catIndex, category) in categories.enumerated() {
            if category.items.contains(normalized) {
                return (catIndex, normalized)
            }
        }
        return (categories.count, normalized)
    }

    // MARK: - TOML parsing

    private static let tableHeaderRE = try! NSRegularExpression(
        pattern: #"^\[([^\]]+)\]$"#
    )

    private static func parse(_ content: String) -> [(name: String, items: [String])] {
        var result: [(name: String, items: [String])] = []
        var currentTable: String?
        // Buffer for multi-line items array values
        var itemsBuffer: String?

        let lines = content.components(separatedBy: .newlines)

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespaces)

            // If we're accumulating a multi-line array, keep appending
            if itemsBuffer != nil {
                itemsBuffer! += " " + trimmed
                if trimmed.contains("]") {
                    if let table = currentTable {
                        let items = parseStringArray(itemsBuffer!)
                        result.append((name: table, items: items))
                    }
                    itemsBuffer = nil
                }
                continue
            }

            // Check for table header: [category]
            let range = NSRange(trimmed.startIndex..., in: trimmed)
            if let match = tableHeaderRE.firstMatch(in: trimmed, range: range),
               let nameRange = Range(match.range(at: 1), in: trimmed)
            {
                currentTable = String(trimmed[nameRange]).trimmingCharacters(in: .whitespaces)
                continue
            }

            // Check for items = [...]
            if trimmed.hasPrefix("items") && trimmed.contains("=") {
                let afterEquals = trimmed.components(separatedBy: "=").dropFirst().joined(separator: "=")
                    .trimmingCharacters(in: .whitespaces)

                if afterEquals.contains("[") && afterEquals.contains("]") {
                    // Single-line array
                    if let table = currentTable {
                        let items = parseStringArray(afterEquals)
                        result.append((name: table, items: items))
                    }
                } else if afterEquals.contains("[") {
                    // Start of multi-line array
                    itemsBuffer = afterEquals
                }
            }
        }

        return result
    }

    /// Parse a TOML-style string array like `["milk", "butter", "eggs"]`
    /// into lowercased string values.
    private static func parseStringArray(_ raw: String) -> [String] {
        // Strip the brackets
        guard let openBracket = raw.firstIndex(of: "["),
              let closeBracket = raw.lastIndex(of: "]") else {
            return []
        }

        let inner = String(raw[raw.index(after: openBracket)..<closeBracket])
        let parts = inner.components(separatedBy: ",")

        return parts.compactMap { part in
            let trimmed = part.trimmingCharacters(in: .whitespaces)
            // Strip surrounding quotes
            let unquoted = trimmed
                .trimmingCharacters(in: CharacterSet(charactersIn: "\""))
                .trimmingCharacters(in: .whitespaces)
            return unquoted.isEmpty ? nil : unquoted.lowercased()
        }
    }
}
