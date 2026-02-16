import SwiftUI

struct RecipeListView: View {
    @Bindable var cookbook: CookbookViewModel
    @Bindable var shoppingList: ShoppingListViewModel
    @State private var searchText = ""
    @State private var selectedRecipe: Recipe?
    @State private var showShoppingList = false

    private var filteredRecipes: [Recipe] {
        if searchText.isEmpty {
            return cookbook.recipes
        }
        return cookbook.recipes.filter {
            $0.name.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationStack {
            List {
                if !shoppingList.sourceRecipeNames.isEmpty && searchText.isEmpty {
                    Section("Added to shopping list") {
                        ForEach(shoppingList.sourceRecipeNames, id: \.self) { name in
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.green)
                                Text(name)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .onDelete { offsets in
                            let names = offsets.map { shoppingList.sourceRecipeNames[$0] }
                            for name in names {
                                shoppingList.removeRecipe(name)
                            }
                        }
                    }
                }

                Section(shoppingList.sourceRecipeNames.isEmpty || !searchText.isEmpty ? "" : "All recipes") {
                    ForEach(filteredRecipes) { recipe in
                        Button {
                            selectedRecipe = recipe
                        } label: {
                            HStack {
                                Text(recipe.name)
                                    .foregroundStyle(.primary)
                                Spacer()
                                if shoppingList.sourceRecipeNames.contains(recipe.name) {
                                    Image(systemName: "checkmark")
                                        .foregroundStyle(.green)
                                        .font(.caption)
                                }
                                Text("\(recipe.ingredients.count) ingredients")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                }
            }
            .searchable(text: $searchText, prompt: "Search recipes")
            .navigationTitle("Recipes")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Menu {
                        Button(role: .destructive) {
                            cookbook.clearCookbook()
                        } label: {
                            Label("Change Cookbook", systemImage: "folder")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showShoppingList = true
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: "cart")
                            if shoppingList.totalCount > 0 {
                                Text("\(shoppingList.totalCount)")
                                    .font(.caption2.bold())
                                    .foregroundStyle(.white)
                                    .padding(.horizontal, 5)
                                    .padding(.vertical, 1)
                                    .background(.red, in: Capsule())
                            }
                        }
                    }
                    .accessibilityIdentifier("cartButton")
                }
            }
            .sheet(isPresented: $showShoppingList) {
                NavigationStack {
                    ShoppingListView(shoppingList: shoppingList)
                }
            }
            .sheet(item: $selectedRecipe) { recipe in
                NavigationStack {
                    IngredientSelectionView(
                        recipe: recipe,
                        shoppingList: shoppingList,
                        onDone: { selectedRecipe = nil }
                    )
                }
            }
            .overlay {
                if cookbook.recipes.isEmpty && !cookbook.isLoading {
                    ContentUnavailableView(
                        "No Recipes",
                        systemImage: "doc.text",
                        description: Text("No .sous recipe files found in the cookbook directory.")
                    )
                }
            }
        }
    }
}
