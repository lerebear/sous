import Foundation
import SwiftUI

@Observable
final class CookbookViewModel {
    var recipes: [Recipe] = []
    var isLoading = false
    var cookbookURL: URL?
    var errorMessage: String?
    var showDirectoryPicker = false

    /// Whether we have a saved cookbook directory
    var hasCookbook: Bool {
        cookbookURL != nil
    }

    /// Try to restore previously bookmarked directory on launch
    func restoreBookmark() {
        if let url = BookmarkManager.resolveBookmark() {
            loadCookbook(from: url)
        }
    }

    /// Load bundled test fixtures (for development/testing)
    func loadBundledRecipes() {
        guard let fixturesURL = Bundle.main.url(forResource: "TestFixtures", withExtension: nil) else {
            errorMessage = "No bundled test fixtures found."
            return
        }
        cookbookURL = fixturesURL
        recipes = SousParser.parseCookbook(from: fixturesURL)
    }

    /// Load recipes from a user-selected directory
    func loadCookbook(from url: URL) {
        isLoading = true
        errorMessage = nil

        let accessing = url.startAccessingSecurityScopedResource()

        defer {
            if accessing {
                url.stopAccessingSecurityScopedResource()
            }
            isLoading = false
        }

        cookbookURL = url
        BookmarkManager.saveBookmark(for: url)

        let parsed = SousParser.parseCookbook(from: url)
        if parsed.isEmpty {
            errorMessage = "No .sous recipe files found in the selected directory."
        }
        recipes = parsed
    }

    /// Change cookbook directory
    func changeCookbook() {
        showDirectoryPicker = true
    }

    /// Clear current cookbook
    func clearCookbook() {
        recipes = []
        cookbookURL = nil
        BookmarkManager.clearBookmark()
    }
}
