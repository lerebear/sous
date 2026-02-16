import SwiftUI

struct ShoppingListView: View {
    @Bindable var shoppingList: ShoppingListViewModel

    var body: some View {
        List {
            if !shoppingList.sourceRecipeNames.isEmpty {
                Section("Recipes") {
                    ForEach(shoppingList.sourceRecipeNames, id: \.self) { name in
                        Label(name, systemImage: "book")
                            .foregroundStyle(.secondary)
                    }
                    .onDelete { offsets in
                        let names = offsets.map { shoppingList.sourceRecipeNames[$0] }
                        for name in names {
                            shoppingList.removeRecipe(name)
                        }
                    }
                }
            }

            if !shoppingList.visibleItems.isEmpty {
                Section("Ingredients") {
                    ForEach(shoppingList.visibleItems) { item in
                        Button {
                            withAnimation {
                                shoppingList.toggleItem(item)
                            }
                        } label: {
                            HStack {
                                Image(systemName: item.isChecked ? "checkmark.circle.fill" : "circle")
                                    .foregroundStyle(item.isChecked ? .green : .secondary)
                                    .imageScale(.large)

                                VStack(alignment: .leading, spacing: 2) {
                                    Text(item.name)
                                        .strikethrough(item.isChecked)
                                        .foregroundStyle(item.isChecked ? .secondary : .primary)

                                    if !item.formattedQuantities.isEmpty {
                                        Text(item.formattedQuantities)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                            .strikethrough(item.isChecked)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        .navigationTitle("Shopping List")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Toggle(isOn: $shoppingList.hideCheckedItems) {
                        Label("Hide Checked Items", systemImage: "eye.slash")
                    }

                    Divider()

                    Button(role: .destructive) {
                        shoppingList.clearChecked()
                    } label: {
                        Label("Clear Checked", systemImage: "trash")
                    }
                    .disabled(shoppingList.items.filter(\.isChecked).isEmpty)

                    Button(role: .destructive) {
                        shoppingList.clearAll()
                    } label: {
                        Label("Clear All", systemImage: "trash.fill")
                    }
                    .disabled(shoppingList.items.isEmpty)
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .overlay {
            if shoppingList.items.isEmpty {
                ContentUnavailableView(
                    "No Items Yet",
                    systemImage: "cart",
                    description: Text("Select recipes and add ingredients to build your shopping list.")
                )
            } else if shoppingList.visibleItems.isEmpty {
                ContentUnavailableView(
                    "All Done!",
                    systemImage: "checkmark.circle",
                    description: Text("All items are checked off. Use the menu to show checked items or clear the list.")
                )
            }
        }
    }
}
