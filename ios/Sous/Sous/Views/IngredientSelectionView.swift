import SwiftUI

struct IngredientSelectionView: View {
    let recipe: Recipe
    @Bindable var shoppingList: ShoppingListViewModel
    let onDone: () -> Void

    @State private var selectedIngredientIDs: Set<String>
    @Environment(\.dismiss) private var dismiss

    init(recipe: Recipe, shoppingList: ShoppingListViewModel, onDone: @escaping () -> Void) {
        self.recipe = recipe
        self.shoppingList = shoppingList
        self.onDone = onDone
        // All ingredients selected by default
        self._selectedIngredientIDs = State(
            initialValue: Set(recipe.ingredients.map(\.id))
        )
    }

    private var selectedCount: Int {
        selectedIngredientIDs.count
    }

    var body: some View {
        List {
            Section {
                ForEach(recipe.ingredients, id: \.id) { ingredient in
                    Button {
                        toggleIngredient(ingredient)
                    } label: {
                        HStack {
                            Image(systemName: selectedIngredientIDs.contains(ingredient.id) ? "checkmark.circle.fill" : "circle")
                                .foregroundStyle(selectedIngredientIDs.contains(ingredient.id) ? .blue : .secondary)
                                .imageScale(.large)

                            VStack(alignment: .leading, spacing: 2) {
                                Text(ingredient.id)
                                    .foregroundStyle(.primary)

                                if ingredient.quantity != nil || ingredient.descriptors != nil || ingredient.preparation != nil {
                                    Text(ingredientDetail(ingredient))
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                }
            } header: {
                HStack {
                    Text("\(selectedCount) of \(recipe.ingredients.count) selected")
                    Spacer()
                    if selectedCount < recipe.ingredients.count {
                        Button("Select All") {
                            selectedIngredientIDs = Set(recipe.ingredients.map(\.id))
                        }
                        .font(.caption)
                    } else {
                        Button("Deselect All") {
                            selectedIngredientIDs.removeAll()
                        }
                        .font(.caption)
                    }
                }
            }
        }
        .navigationTitle(recipe.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Cancel") {
                    dismiss()
                    onDone()
                }
            }

            ToolbarItem(placement: .confirmationAction) {
                Button("Add to List") {
                    let selected = recipe.ingredients.filter {
                        selectedIngredientIDs.contains($0.id)
                    }
                    shoppingList.addIngredients(selected, from: recipe.name)
                    dismiss()
                    onDone()
                }
                .bold()
                .disabled(selectedIngredientIDs.isEmpty)
            }
        }
    }

    private func toggleIngredient(_ ingredient: Ingredient) {
        if selectedIngredientIDs.contains(ingredient.id) {
            selectedIngredientIDs.remove(ingredient.id)
        } else {
            selectedIngredientIDs.insert(ingredient.id)
        }
    }

    private func ingredientDetail(_ ingredient: Ingredient) -> String {
        [ingredient.quantity, ingredient.descriptors, ingredient.preparation]
            .compactMap { $0?.isEmpty == false ? $0 : nil }
            .joined(separator: " · ")
    }
}
