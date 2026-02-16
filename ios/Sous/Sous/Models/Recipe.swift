import Foundation

struct Recipe: Identifiable {
    let id = UUID()
    let name: String
    let ingredients: [Ingredient]
    let filePath: String
}
