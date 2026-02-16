import XCTest

final class SousUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--use-bundled-recipes"]
        app.launch()
    }

    // MARK: - Recipe list

    func testRecipeListShowsBundledRecipes() {
        XCTAssertTrue(app.navigationBars["Recipes"].exists)
        XCTAssertTrue(app.staticTexts["Mapo Tofu"].exists)
        XCTAssertTrue(app.staticTexts["Pozole Verde"].exists)
        XCTAssertTrue(app.staticTexts["Roasted broccoli"].exists)
    }

    // MARK: - Ingredient selection and recipe tracking

    func testSelectRecipeAndAddIngredients() {
        // Tap a recipe to open ingredient selection
        app.staticTexts["Roasted broccoli"].tap()

        // Verify ingredient selection sheet appeared
        let addButton = app.buttons["Add to List"]
        XCTAssertTrue(addButton.waitForExistence(timeout: 2))

        // Verify ingredients are listed
        XCTAssertTrue(app.staticTexts["broccoli crowns"].exists)
        XCTAssertTrue(app.staticTexts["olive oil"].exists)

        // Add all ingredients to shopping list
        addButton.tap()

        // Back on recipe list — verify we returned
        XCTAssertTrue(app.navigationBars["Recipes"].waitForExistence(timeout: 3))
    }

    // MARK: - Shopping cart navigation

    func testCartButtonNavigatesToShoppingList() {
        // First add some ingredients
        app.staticTexts["Roasted broccoli"].tap()
        let addButton = app.buttons["Add to List"]
        XCTAssertTrue(addButton.waitForExistence(timeout: 2))
        addButton.tap()

        // Wait for sheet to dismiss and recipe list to reappear
        XCTAssertTrue(app.navigationBars["Recipes"].waitForExistence(timeout: 3))

        // Tap the cart button
        let cartButton = app.buttons["cartButton"]
        XCTAssertTrue(cartButton.waitForExistence(timeout: 2), "Cart button should exist")
        cartButton.tap()

        // Verify the shopping list sheet appeared (look for the Shopping List nav title)
        XCTAssertTrue(app.navigationBars["Shopping List"].waitForExistence(timeout: 3))

        // Verify the source recipe name appears on the shopping list
        XCTAssertTrue(app.staticTexts["Roasted broccoli"].exists)

        // Verify ingredients appear
        XCTAssertTrue(app.staticTexts["broccoli crowns"].exists)
        XCTAssertTrue(app.staticTexts["olive oil"].exists)
    }

    // MARK: - Multiple recipes

    func testMultipleRecipesTracked() {
        // Add Roasted broccoli
        app.staticTexts["Roasted broccoli"].tap()
        var addButton = app.buttons["Add to List"]
        XCTAssertTrue(addButton.waitForExistence(timeout: 2))
        addButton.tap()
        XCTAssertTrue(app.navigationBars["Recipes"].waitForExistence(timeout: 3))

        // Add Mapo Tofu
        app.staticTexts["Mapo Tofu"].tap()
        addButton = app.buttons["Add to List"]
        XCTAssertTrue(addButton.waitForExistence(timeout: 2))
        addButton.tap()
        XCTAssertTrue(app.navigationBars["Recipes"].waitForExistence(timeout: 3))

        // Navigate to shopping list
        let cartButton = app.buttons["cartButton"]
        XCTAssertTrue(cartButton.waitForExistence(timeout: 2))
        cartButton.tap()
        XCTAssertTrue(app.navigationBars["Shopping List"].waitForExistence(timeout: 3))

        // Both recipe names should appear in the shopping list
        XCTAssertTrue(app.staticTexts["Roasted broccoli"].exists)
        XCTAssertTrue(app.staticTexts["Mapo Tofu"].exists)

        // Ingredients from both recipes should be present (scroll to find them)
        let tofuText = app.staticTexts["medium or medium-firm tofu"]
        if !tofuText.exists {
            app.swipeUp()
        }
        XCTAssertTrue(tofuText.waitForExistence(timeout: 2))
    }
}
