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
            } else if let path = Self.launchArgumentValue(for: "--cookbook-path") {
                cookbook.loadCookbook(from: URL(fileURLWithPath: path))
            } else {
                cookbook.restoreBookmark()
            }
        }
    }

    private static func launchArgumentValue(for key: String) -> String? {
        let args = ProcessInfo.processInfo.arguments
        guard let index = args.firstIndex(of: key), index + 1 < args.count else { return nil }
        return args[index + 1]
    }
}
