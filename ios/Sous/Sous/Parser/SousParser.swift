import Foundation

enum SousParser {
    // MARK: - Regex patterns matching the Python implementation
    // Using NSRegularExpression because Swift regex literals can't handle curly braces in patterns.

    private static let headerRE = try! NSRegularExpression(pattern: #"^(#+)\s+(.+)$"#)
    private static let attributeRE = try! NSRegularExpression(pattern: #"^@([\w-]+)\s+(.+)$"#)
    private static let commentRE = try! NSRegularExpression(pattern: #"^%\s+(.+)$"#)
    private static let blockIngredientRE = try! NSRegularExpression(
        pattern: #"^\{([^}]*)\}([^\[]*)\[([^,\]]+)\](.*)$"#
    )
    private static let inlineIngredientRE = try! NSRegularExpression(
        pattern: #"\{([^}]*)\}\[([^,\]]+)\]"#
    )

    // MARK: - Public API

    static func parseRecipe(from content: String, filePath: String = "") -> Recipe? {
        let lines = content.components(separatedBy: .newlines)
        var recipeName: String?
        var ingredients: [Ingredient] = []

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespaces)
            guard !trimmed.isEmpty else { continue }
            let range = NSRange(trimmed.startIndex..., in: trimmed)

            // Header
            if recipeName == nil, let match = headerRE.firstMatch(in: trimmed, range: range) {
                if let nameRange = Range(match.range(at: 2), in: trimmed) {
                    recipeName = String(trimmed[nameRange])
                }
                continue
            }

            // Attribute
            if attributeRE.firstMatch(in: trimmed, range: range) != nil { continue }

            // Comment
            if commentRE.firstMatch(in: trimmed, range: range) != nil { continue }

            // Block ingredient
            if let ingredient = parseBlockIngredient(trimmed, range: range) {
                ingredients.append(ingredient)
                continue
            }

            // Inline ingredients from prose
            ingredients.append(contentsOf: parseInlineIngredients(trimmed, range: range))
        }

        guard let name = recipeName else { return nil }

        // Deduplicate ingredients by id, preserving order of first occurrence
        var seen = Set<String>()
        let uniqueIngredients = ingredients.filter { ingredient in
            if seen.contains(ingredient.id) { return false }
            seen.insert(ingredient.id)
            return true
        }

        return Recipe(name: name, ingredients: uniqueIngredients, filePath: filePath)
    }

    static func parseRecipe(from url: URL) -> Recipe? {
        guard let content = try? String(contentsOf: url, encoding: .utf8) else {
            return nil
        }
        return parseRecipe(from: content, filePath: url.path)
    }

    static func parseCookbook(from directoryURL: URL) -> [Recipe] {
        var recipes: [Recipe] = []

        guard let enumerator = FileManager.default.enumerator(
            at: directoryURL,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        ) else {
            return recipes
        }

        for case let fileURL as URL in enumerator {
            guard fileURL.pathExtension == "sous" else { continue }
            if let recipe = parseRecipe(from: fileURL) {
                recipes.append(recipe)
            }
        }

        return recipes.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    // MARK: - Private helpers

    private static func parseBlockIngredient(_ line: String, range: NSRange) -> Ingredient? {
        guard let match = blockIngredientRE.firstMatch(in: line, range: range) else {
            return nil
        }

        let quantity = extractGroup(match, at: 1, in: line) ?? ""
        let descriptors = (extractGroup(match, at: 2, in: line) ?? "")
            .trimmingCharacters(in: .punctuationCharacters)
            .trimmingCharacters(in: .whitespaces)
        let id = extractGroup(match, at: 3, in: line) ?? ""
        let preparation = (extractGroup(match, at: 4, in: line) ?? "")
            .trimmingCharacters(in: .punctuationCharacters)
            .trimmingCharacters(in: .whitespaces)

        return Ingredient(
            id: id,
            quantity: quantity.isEmpty ? nil : quantity,
            descriptors: descriptors.isEmpty ? nil : descriptors,
            preparation: preparation.isEmpty ? nil : preparation
        )
    }

    private static func parseInlineIngredients(_ line: String, range: NSRange) -> [Ingredient] {
        let matches = inlineIngredientRE.matches(in: line, range: range)
        return matches.map { match in
            let quantity = extractGroup(match, at: 1, in: line) ?? ""
            let id = extractGroup(match, at: 2, in: line) ?? ""
            return Ingredient(
                id: id,
                quantity: quantity.isEmpty ? nil : quantity,
                descriptors: nil,
                preparation: nil
            )
        }
    }

    private static func extractGroup(_ match: NSTextCheckingResult, at index: Int, in string: String) -> String? {
        let nsRange = match.range(at: index)
        guard nsRange.location != NSNotFound, let range = Range(nsRange, in: string) else {
            return nil
        }
        return String(string[range])
    }
}
