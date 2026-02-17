import Foundation
import SwiftUI

@Observable
final class ShoppingListViewModel {
    var items: [ShoppingListItem] = []
    var hideCheckedItems = false
    var config: ShoppingListConfig?
    private(set) var sourceRecipeNames: [String] = []

    /// Ingredients contributed by each recipe (keyed by recipe name)
    private var ingredientsByRecipe: [String: [Ingredient]] = [:]

    /// Number of unchecked items
    var remainingCount: Int {
        items.filter { !$0.isChecked }.count
    }

    /// Total number of items
    var totalCount: Int {
        items.count
    }

    /// Items to display based on hide setting
    var visibleItems: [ShoppingListItem] {
        if hideCheckedItems {
            return items.filter { !$0.isChecked }
        }
        return items
    }

    /// Items grouped by category when a config is active, or a single nil-keyed group otherwise.
    var groupedItems: [(category: String?, items: [ShoppingListItem])] {
        let visible = visibleItems

        guard let config else {
            return [(category: nil, items: visible)]
        }

        if visible.isEmpty { return [] }

        var grouped: [(category: String?, items: [ShoppingListItem])] = []
        var currentCategory = ""  // sentinel that won't match any real category

        for item in visible {
            let displayCategory = config.category(for: item.name) ?? "other"

            if displayCategory != currentCategory || grouped.isEmpty {
                grouped.append((category: displayCategory, items: [item]))
                currentCategory = displayCategory
            } else {
                grouped[grouped.count - 1].items.append(item)
            }
        }

        return grouped
    }

    /// Add ingredients from a recipe selection to the shopping list
    func addIngredients(_ ingredients: [Ingredient], from recipeName: String) {
        if !sourceRecipeNames.contains(recipeName) {
            sourceRecipeNames.append(recipeName)
        }
        ingredientsByRecipe[recipeName] = ingredients
        rebuildItems()
    }

    /// Remove a recipe and its ingredients from the shopping list
    func removeRecipe(_ recipeName: String) {
        sourceRecipeNames.removeAll { $0 == recipeName }
        ingredientsByRecipe.removeValue(forKey: recipeName)
        rebuildItems()
    }

    /// Toggle checked state for an item
    func toggleItem(_ item: ShoppingListItem) {
        guard let index = items.firstIndex(where: { $0.id == item.id }) else { return }
        items[index].isChecked.toggle()
    }

    /// Clear all checked items
    func clearChecked() {
        items.removeAll { $0.isChecked }
    }

    /// Clear all items
    func clearAll() {
        items.removeAll()
        sourceRecipeNames.removeAll()
        ingredientsByRecipe.removeAll()
    }

    /// Apply a config and re-sort items accordingly
    func applyConfig(_ newConfig: ShoppingListConfig?) {
        config = newConfig
        rebuildItems()
    }

    /// Rebuild the items list from all tracked recipe ingredients
    private func rebuildItems() {
        // Collect all ingredients across all recipes
        var quantitiesByName: [String: [String]] = [:]
        for (_, ingredients) in ingredientsByRecipe {
            for ingredient in ingredients {
                let qty = (ingredient.quantity?.isEmpty == false) ? ingredient.quantity! : nil
                if var existing = quantitiesByName[ingredient.id] {
                    if let qty { existing.append(qty) }
                    quantitiesByName[ingredient.id] = existing
                } else {
                    quantitiesByName[ingredient.id] = qty.map { [$0] } ?? []
                }
            }
        }

        // Preserve check state and order of existing items
        let checkedNames = Set(items.filter(\.isChecked).map(\.name))

        var newItems: [ShoppingListItem] = []
        var seen = Set<String>()

        // Keep existing items that are still present (preserves order)
        for item in items {
            if quantitiesByName[item.name] != nil {
                newItems.append(ShoppingListItem(
                    name: item.name,
                    quantities: quantitiesByName[item.name]!,
                    isChecked: checkedNames.contains(item.name)
                ))
                seen.insert(item.name)
            }
        }

        // Add new ingredients in sorted order
        let newNames = quantitiesByName.keys.filter { !seen.contains($0) }.sorted()
        for name in newNames {
            newItems.append(ShoppingListItem(
                name: name,
                quantities: quantitiesByName[name] ?? [],
                isChecked: false
            ))
        }

        // Sort by config if available, otherwise alphabetically
        if let config {
            newItems.sort { a, b in
                config.sortKey(for: a.name) < config.sortKey(for: b.name)
            }
        } else {
            newItems.sort { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
        }

        items = newItems
    }
}
