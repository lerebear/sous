import SwiftUI

struct ContentView: View {
    @State private var cookbook = CookbookViewModel()
    @State private var shoppingList = ShoppingListViewModel()

    var body: some View {
        Group {
            if cookbook.hasCookbook {
                RecipeListView(cookbook: cookbook, shoppingList: shoppingList)
            } else {
                CookbookPickerView(cookbook: cookbook)
            }
        }
        .onAppear {
            if ProcessInfo.processInfo.arguments.contains("--use-bundled-recipes") {
                cookbook.loadBundledRecipes()
            } else {
                cookbook.restoreBookmark()
            }
        }
    }
}
