import XCTest
@testable import Sous

final class SousParserTests: XCTestCase {

    // MARK: - Block ingredient parsing

    func testParseSimpleBlockIngredient() {
        let content = """
        # Test Recipe

        {2} large [broccoli crowns], washed and trimmed
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertNotNil(recipe)
        XCTAssertEqual(recipe?.name, "Test Recipe")
        XCTAssertEqual(recipe?.ingredients.count, 1)

        let ingredient = recipe?.ingredients.first
        XCTAssertEqual(ingredient?.id, "broccoli crowns")
        XCTAssertEqual(ingredient?.quantity, "2")
        XCTAssertEqual(ingredient?.descriptors, "large")
        XCTAssertEqual(ingredient?.preparation, "washed and trimmed")
    }

    func testParseBlockIngredientWithEmptyQuantity() {
        let content = """
        # Test Recipe

        {} extra virgin [olive oil]
        """

        let recipe = SousParser.parseRecipe(from: content)
        let ingredient = recipe?.ingredients.first
        XCTAssertEqual(ingredient?.id, "olive oil")
        XCTAssertNil(ingredient?.quantity)
        XCTAssertEqual(ingredient?.descriptors, "extra virgin")
        XCTAssertNil(ingredient?.preparation)
    }

    func testParseBlockIngredientMinimal() {
        let content = """
        # Test Recipe

        {}[red pepper flakes]
        """

        let recipe = SousParser.parseRecipe(from: content)
        let ingredient = recipe?.ingredients.first
        XCTAssertEqual(ingredient?.id, "red pepper flakes")
        XCTAssertNil(ingredient?.quantity)
        XCTAssertNil(ingredient?.descriptors)
        XCTAssertNil(ingredient?.preparation)
    }

    func testParseBlockIngredientWithFraction() {
        let content = """
        # Test Recipe

        {1/2}[lemon], for juicing
        """

        let recipe = SousParser.parseRecipe(from: content)
        let ingredient = recipe?.ingredients.first
        XCTAssertEqual(ingredient?.id, "lemon")
        XCTAssertEqual(ingredient?.quantity, "1/2")
        XCTAssertEqual(ingredient?.preparation, "for juicing")
    }

    // MARK: - Inline ingredient parsing

    func testParseInlineIngredients() {
        let content = """
        # Test Recipe

        Season with {}[kosher salt] and freshly ground {}[black pepper].
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertEqual(recipe?.ingredients.count, 2)
        XCTAssertEqual(recipe?.ingredients[0].id, "kosher salt")
        XCTAssertEqual(recipe?.ingredients[1].id, "black pepper")
    }

    func testParseInlineIngredientWithQuantity() {
        let content = """
        # Test Recipe

        Add {2 tablespoons}[soy sauce] to the pan.
        """

        let recipe = SousParser.parseRecipe(from: content)
        let ingredient = recipe?.ingredients.first
        XCTAssertEqual(ingredient?.id, "soy sauce")
        XCTAssertEqual(ingredient?.quantity, "2 tablespoons")
    }

    // MARK: - Recipe-level parsing

    func testRecipeNameFromHeader() {
        let content = """
        # Roasted Broccoli

        @author Test Author
        @syntax 1
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertEqual(recipe?.name, "Roasted Broccoli")
    }

    func testRecipeWithNoHeaderReturnsNil() {
        let content = """
        @author Test Author

        {2}[broccoli]
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertNil(recipe)
    }

    func testSkipsAttributes() {
        let content = """
        # Test Recipe

        @source https://example.com
        @author Test
        @syntax 1

        {2}[broccoli]
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertEqual(recipe?.ingredients.count, 1)
    }

    func testSkipsComments() {
        let content = """
        # Test Recipe

        % This is a comment
        {2}[broccoli]
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertEqual(recipe?.ingredients.count, 1)
    }

    // MARK: - Deduplication

    func testDeduplicatesIngredientsByID() {
        let content = """
        # Test Recipe

        {3 cloves} [garlic], minced

        Add [garlic] to the pan with {1 tablespoon}[garlic] powder.
        """

        let recipe = SousParser.parseRecipe(from: content)
        // "garlic" appears as block + inline, but should only appear once after dedup
        // "garlic" (block) and "garlic" (inline reference with quantity) — deduped by id
        let garlicIngredients = recipe?.ingredients.filter { $0.id == "garlic" }
        XCTAssertEqual(garlicIngredients?.count, 1)
    }

    // MARK: - Full recipe fixture parsing

    func testParseRoastedBroccoliFixture() {
        let content = """
        # Roasted broccoli

        @author Lérè Williams
        @syntax 1

        {2} large [broccoli crowns], washed and trimmed
        {3} large [garlic cloves], minced
        {} extra virgin [olive oil]
        {}[red pepper flakes]
        {1/2}[lemon], for juicing

        Pre-heat oven to 415 F.

        Place trimmed [broccoli] in a large bowl and season with [garlic], [red pepper flakes], {}[kosher salt] and freshly ground {}[black pepper]. Toss with [olive oil] and mix until ingredients are well combined.

        Transfer broccoli to a parchment-lined baking sheet and roast for 20 minutes, flipping broccoli halfway through to achieve an even char.

        Remove baking sheet from oven. Squeeze [lemon] juice evenly over the broccoli. Serve warm.
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertNotNil(recipe)
        XCTAssertEqual(recipe?.name, "Roasted broccoli")

        let ids = recipe?.ingredients.map(\.id)
        XCTAssertEqual(ids, [
            "broccoli crowns",
            "garlic cloves",
            "olive oil",
            "red pepper flakes",
            "lemon",
            "kosher salt",
            "black pepper"
        ])

        // Check specific ingredient details
        let broccoli = recipe?.ingredients.first { $0.id == "broccoli crowns" }
        XCTAssertEqual(broccoli?.quantity, "2")
        XCTAssertEqual(broccoli?.descriptors, "large")
        XCTAssertEqual(broccoli?.preparation, "washed and trimmed")
    }

    func testParseMaPoTofuFixture() {
        let content = """
        # Mapo Tofu

        @source https://cooking.nytimes.com/recipes/1021459-mapo-tofu
        @author Andrea Nguyen
        @total-time 30
        @yield 4 cups
        @syntax 1

        You can order mapo tofu from many Chinese restaurants.

        {16 ounces}[medium or medium-firm tofu]
        {1 rounded teaspoon}[sichuan peppercorns]
        {3 tablespoons}[canola oil]
        {6 ounces}[ground beef or pork] roughly chopped to loosen
        {2.5-3 tablespoons}[doubanjiang]
        {1 tablespoon}[douchi]
        {1 teaspoon}[fresh ginger] minced
        {0.5 teaspoons}[red pepper flakes]
        {2 teaspoons}[regular soy sauce]
        {1 rounded teaspoon}[granulated sugar]
        {}[fine sea salt]
        {2}[scallions] trimmed and cut on a sharp bias into thin
        {1.5 tablespoons}[cornstarch] dissolved in 3 tablespoons water
        {}[white rice] Cooked
        """

        let recipe = SousParser.parseRecipe(from: content)
        XCTAssertNotNil(recipe)
        XCTAssertEqual(recipe?.name, "Mapo Tofu")
        XCTAssertEqual(recipe?.ingredients.count, 14)

        let tofu = recipe?.ingredients.first { $0.id == "medium or medium-firm tofu" }
        XCTAssertEqual(tofu?.quantity, "16 ounces")
    }

    // MARK: - Shopping list recipe tracking

    func testAddIngredientsTracksRecipeName() {
        let vm = ShoppingListViewModel()
        let ingredients = [Ingredient(id: "salt", quantity: nil, descriptors: nil, preparation: nil)]

        vm.addIngredients(ingredients, from: "Roasted broccoli")
        XCTAssertEqual(vm.sourceRecipeNames, ["Roasted broccoli"])

        // Adding from same recipe doesn't duplicate
        vm.addIngredients(ingredients, from: "Roasted broccoli")
        XCTAssertEqual(vm.sourceRecipeNames, ["Roasted broccoli"])

        // Adding from different recipe appends
        vm.addIngredients(ingredients, from: "Mapo Tofu")
        XCTAssertEqual(vm.sourceRecipeNames, ["Roasted broccoli", "Mapo Tofu"])
    }

    func testClearAllResetsRecipeNames() {
        let vm = ShoppingListViewModel()
        let ingredients = [Ingredient(id: "salt", quantity: "1 tsp", descriptors: nil, preparation: nil)]

        vm.addIngredients(ingredients, from: "Roasted broccoli")
        vm.addIngredients(ingredients, from: "Mapo Tofu")
        XCTAssertEqual(vm.sourceRecipeNames.count, 2)

        vm.clearAll()
        XCTAssertTrue(vm.sourceRecipeNames.isEmpty)
        XCTAssertTrue(vm.items.isEmpty)
    }

    func testClearCheckedPreservesRecipeNames() {
        let vm = ShoppingListViewModel()
        let ingredients = [Ingredient(id: "salt", quantity: "1 tsp", descriptors: nil, preparation: nil)]

        vm.addIngredients(ingredients, from: "Roasted broccoli")
        vm.toggleItem(vm.items[0])
        vm.clearChecked()

        // Recipe names are preserved even after clearing checked items
        XCTAssertEqual(vm.sourceRecipeNames, ["Roasted broccoli"])
    }

    func testRemoveRecipeRemovesExclusiveIngredients() {
        let vm = ShoppingListViewModel()
        let broccoliIngredients = [
            Ingredient(id: "broccoli", quantity: "2", descriptors: nil, preparation: nil),
            Ingredient(id: "salt", quantity: "1 tsp", descriptors: nil, preparation: nil),
        ]
        let tofuIngredients = [
            Ingredient(id: "tofu", quantity: "16 oz", descriptors: nil, preparation: nil),
            Ingredient(id: "salt", quantity: "0.5 tsp", descriptors: nil, preparation: nil),
        ]

        vm.addIngredients(broccoliIngredients, from: "Roasted broccoli")
        vm.addIngredients(tofuIngredients, from: "Mapo Tofu")
        XCTAssertEqual(vm.items.count, 3) // broccoli, salt, tofu

        // Remove Roasted broccoli — "broccoli" should go, "salt" should stay (shared)
        vm.removeRecipe("Roasted broccoli")
        XCTAssertEqual(vm.sourceRecipeNames, ["Mapo Tofu"])

        let itemNames = vm.items.map(\.name).sorted()
        XCTAssertEqual(itemNames, ["salt", "tofu"])

        // Salt should now only have Mapo Tofu's quantity
        let salt = vm.items.first { $0.name == "salt" }
        XCTAssertEqual(salt?.quantities, ["0.5 tsp"])
    }

    func testRemoveLastRecipeClearsEverything() {
        let vm = ShoppingListViewModel()
        let ingredients = [Ingredient(id: "salt", quantity: "1 tsp", descriptors: nil, preparation: nil)]

        vm.addIngredients(ingredients, from: "Roasted broccoli")
        XCTAssertEqual(vm.items.count, 1)

        vm.removeRecipe("Roasted broccoli")
        XCTAssertTrue(vm.sourceRecipeNames.isEmpty)
        XCTAssertTrue(vm.items.isEmpty)
    }

    // MARK: - Bundled fixture parsing

    func testParseBundledFixtures() {
        guard let fixturesURL = Bundle(for: Self.self).url(forResource: "TestFixtures", withExtension: nil) else {
            // Fixtures may not be in test bundle — skip gracefully
            return
        }

        let recipes = SousParser.parseCookbook(from: fixturesURL)
        XCTAssertGreaterThan(recipes.count, 0, "Should parse at least one recipe from fixtures")

        for recipe in recipes {
            XCTAssertFalse(recipe.name.isEmpty, "Recipe should have a name")
            XCTAssertFalse(recipe.ingredients.isEmpty, "Recipe '\(recipe.name)' should have ingredients")
        }
    }
}
