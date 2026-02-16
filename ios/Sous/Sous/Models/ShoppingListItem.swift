import Foundation

struct ShoppingListItem: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let quantities: [String]
    var isChecked: Bool = false

    var formattedQuantities: String {
        if quantities.isEmpty {
            return ""
        }
        return "(\(quantities.joined(separator: ", ")))"
    }

    var displayText: String {
        let qty = formattedQuantities
        if qty.isEmpty {
            return name
        }
        return "\(name) \(qty)"
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(name)
    }

    static func == (lhs: ShoppingListItem, rhs: ShoppingListItem) -> Bool {
        lhs.name == rhs.name
    }
}
