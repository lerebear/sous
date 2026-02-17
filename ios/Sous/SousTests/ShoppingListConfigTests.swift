import XCTest
@testable import Sous

final class ShoppingListConfigTests: XCTestCase {

    // MARK: - TOML parsing

    func testParsesCategories() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk", "butter"]

        [produce]
        items = ["potatoes", "onions"]
        """)

        XCTAssertEqual(config.categories.count, 2)
        XCTAssertEqual(config.categories[0].name, "dairy")
        XCTAssertEqual(config.categories[0].items, ["milk", "butter"])
        XCTAssertEqual(config.categories[1].name, "produce")
        XCTAssertEqual(config.categories[1].items, ["potatoes", "onions"])
    }

    func testParsesMultiLineArray() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = [
            "milk",
            "butter",
            "eggs"
        ]
        """)

        XCTAssertEqual(config.categories.count, 1)
        XCTAssertEqual(config.categories[0].items, ["milk", "butter", "eggs"])
    }

    func testIgnoresNonItemKeys() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk"]
        other_key = "ignored"
        """)

        XCTAssertEqual(config.categories.count, 1)
        XCTAssertEqual(config.categories[0].items, ["milk"])
    }

    // MARK: - Category lookup

    func testCategoryForKnownItem() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk", "butter"]

        [produce]
        items = ["potatoes"]
        """)

        XCTAssertEqual(config.category(for: "milk"), "dairy")
        XCTAssertEqual(config.category(for: "potatoes"), "produce")
    }

    func testCategoryForIsCaseInsensitive() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["Milk"]
        """)

        XCTAssertEqual(config.category(for: "milk"), "dairy")
        XCTAssertEqual(config.category(for: "MILK"), "dairy")
    }

    func testCategoryForUnknownItemReturnsNil() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk"]
        """)

        XCTAssertNil(config.category(for: "garlic"))
    }

    // MARK: - Sort key ordering

    func testSortKeyOrdersByCategoryThenAlphabetically() {
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk", "butter"]

        [produce]
        items = ["potatoes", "onions"]
        """)

        // dairy before produce
        XCTAssertTrue(config.sortKey(for: "butter") < config.sortKey(for: "onions"))
        // within dairy, butter before milk (alphabetically)
        XCTAssertTrue(config.sortKey(for: "butter") < config.sortKey(for: "milk"))
        // within produce, onions before potatoes (alphabetically)
        XCTAssertTrue(config.sortKey(for: "onions") < config.sortKey(for: "potatoes"))
        // uncategorized last
        XCTAssertTrue(config.sortKey(for: "milk") < config.sortKey(for: "garlic"))
    }

    // MARK: - ViewModel integration

    func testApplyConfigSortsItems() {
        let vm = ShoppingListViewModel()
        let ingredients = [
            Ingredient(id: "potatoes", quantity: "3", descriptors: nil, preparation: nil),
            Ingredient(id: "milk", quantity: "1 cup", descriptors: nil, preparation: nil),
            Ingredient(id: "butter", quantity: nil, descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(ingredients, from: "Test Recipe")

        // Without config, items are sorted alphabetically
        XCTAssertEqual(vm.items.map(\.name), ["butter", "milk", "potatoes"])

        // Apply config — dairy items first (alphabetically), then produce
        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk", "butter"]

        [produce]
        items = ["potatoes"]
        """)
        vm.applyConfig(config)

        XCTAssertEqual(vm.items.map(\.name), ["butter", "milk", "potatoes"])
    }

    func testApplyConfigPutsUncategorizedItemsLast() {
        let vm = ShoppingListViewModel()
        let ingredients = [
            Ingredient(id: "garlic", quantity: "3 cloves", descriptors: nil, preparation: nil),
            Ingredient(id: "milk", quantity: "1 cup", descriptors: nil, preparation: nil),
            Ingredient(id: "olive oil", quantity: nil, descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(ingredients, from: "Test Recipe")

        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk"]
        """)
        vm.applyConfig(config)

        XCTAssertEqual(vm.items.map(\.name), ["milk", "garlic", "olive oil"])
    }

    func testGroupedItemsWithConfig() {
        let vm = ShoppingListViewModel()
        let ingredients = [
            Ingredient(id: "milk", quantity: "1 cup", descriptors: nil, preparation: nil),
            Ingredient(id: "garlic", quantity: "3 cloves", descriptors: nil, preparation: nil),
            Ingredient(id: "potatoes", quantity: "2", descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(ingredients, from: "Test Recipe")

        let config = ShoppingListConfig(from: """
        [dairy]
        items = ["milk"]

        [produce]
        items = ["potatoes"]
        """)
        vm.applyConfig(config)

        let groups = vm.groupedItems
        XCTAssertEqual(groups.count, 3)
        XCTAssertEqual(groups[0].category, "dairy")
        XCTAssertEqual(groups[0].items.map(\.name), ["milk"])
        XCTAssertEqual(groups[1].category, "produce")
        XCTAssertEqual(groups[1].items.map(\.name), ["potatoes"])
        XCTAssertEqual(groups[2].category, "other")
        XCTAssertEqual(groups[2].items.map(\.name), ["garlic"])
    }

    func testGroupedItemsWithoutConfig() {
        let vm = ShoppingListViewModel()
        let ingredients = [
            Ingredient(id: "milk", quantity: "1 cup", descriptors: nil, preparation: nil),
            Ingredient(id: "garlic", quantity: "3 cloves", descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(ingredients, from: "Test Recipe")

        let groups = vm.groupedItems
        XCTAssertEqual(groups.count, 1)
        XCTAssertNil(groups[0].category)
        XCTAssertEqual(groups[0].items.count, 2)
    }

    func testRemoveConfigRestoresAlphabeticalOrder() {
        let vm = ShoppingListViewModel()
        let ingredients = [
            Ingredient(id: "butter", quantity: nil, descriptors: nil, preparation: nil),
            Ingredient(id: "milk", quantity: "1 cup", descriptors: nil, preparation: nil),
            Ingredient(id: "potatoes", quantity: "3", descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(ingredients, from: "Test Recipe")

        // With config: produce first, then other (alphabetically)
        let config = ShoppingListConfig(from: """
        [produce]
        items = ["potatoes"]
        """)
        vm.applyConfig(config)
        XCTAssertEqual(vm.items.map(\.name), ["potatoes", "butter", "milk"])

        // Remove config — all items sorted alphabetically
        vm.applyConfig(nil)
        XCTAssertEqual(vm.items.map(\.name), ["butter", "milk", "potatoes"])
    }
}
