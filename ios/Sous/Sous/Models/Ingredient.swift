import Foundation

struct Ingredient: Identifiable, Hashable {
    let id: String
    let quantity: String?
    let descriptors: String?
    let preparation: String?

    var displayName: String {
        [quantity, descriptors, id, preparation]
            .compactMap { $0?.isEmpty == false ? $0 : nil }
            .joined(separator: " ")
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    static func == (lhs: Ingredient, rhs: Ingredient) -> Bool {
        lhs.id == rhs.id
            && lhs.quantity == rhs.quantity
            && lhs.descriptors == rhs.descriptors
            && lhs.preparation == rhs.preparation
    }
}
