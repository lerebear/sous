import SwiftUI

struct ShoppingListView: View {
    @Bindable var shoppingList: ShoppingListViewModel
    var cookbookURL: URL?

    @State private var availableConfigs: [(name: String, url: URL)] = []
    @State private var activeConfigName: String?
    @State private var collapsedSections: Set<String> = []

    private var hasConfig: Bool { shoppingList.config != nil }

    private var allSectionNames: [String] {
        shoppingList.groupedItems.compactMap(\.category)
    }

    private var allCollapsed: Bool {
        let names = allSectionNames
        return !names.isEmpty && names.allSatisfy { collapsedSections.contains($0) }
    }

    var body: some View {
        List {
            if !shoppingList.sourceRecipeNames.isEmpty {
                Section("Recipes") {
                    ForEach(shoppingList.sourceRecipeNames, id: \.self) { name in
                        Label(name, systemImage: "book")
                            .foregroundStyle(.secondary)
                    }
                    .onDelete { offsets in
                        let names = offsets.map { shoppingList.sourceRecipeNames[$0] }
                        for name in names {
                            shoppingList.removeRecipe(name)
                        }
                    }
                }
            }

            if !shoppingList.visibleItems.isEmpty {
                let groups = shoppingList.groupedItems

                if hasConfig {
                    ForEach(Array(groups.enumerated()), id: \.offset) { _, group in
                        let sectionName = group.category ?? "other"
                        Section {
                            if !collapsedSections.contains(sectionName) {
                                ForEach(group.items) { item in
                                    shoppingListItemRow(item)
                                }
                            }
                        } header: {
                            Button {
                                withAnimation {
                                    toggleSection(sectionName)
                                }
                            } label: {
                                HStack {
                                    Text(sectionName)
                                    Spacer()
                                    Image(systemName: collapsedSections.contains(sectionName) ? "chevron.right" : "chevron.down")
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                } else {
                    Section("Ingredients") {
                        ForEach(groups.first?.items ?? []) { item in
                            shoppingListItemRow(item)
                        }
                    }
                }
            }
        }
        .navigationTitle("Shopping List")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Toggle(isOn: $shoppingList.hideCheckedItems) {
                        Label("Hide Checked Items", systemImage: "eye.slash")
                    }

                    if !availableConfigs.isEmpty {
                        Divider()

                        Menu {
                            Button {
                                shoppingList.applyConfig(nil)
                                activeConfigName = nil
                                collapsedSections.removeAll()
                            } label: {
                                if activeConfigName == nil {
                                    Label("None", systemImage: "checkmark")
                                } else {
                                    Text("None")
                                }
                            }

                            ForEach(availableConfigs, id: \.url) { config in
                                Button {
                                    loadConfig(config)
                                } label: {
                                    if activeConfigName == config.name {
                                        Label(config.name, systemImage: "checkmark")
                                    } else {
                                        Text(config.name)
                                    }
                                }
                            }
                        } label: {
                            Label("Organize By", systemImage: "list.bullet.indent")
                        }
                    }

                    if hasConfig && !shoppingList.visibleItems.isEmpty {
                        Divider()

                        Button {
                            withAnimation {
                                toggleAllSections()
                            }
                        } label: {
                            if allCollapsed {
                                Label("Expand All", systemImage: "arrow.down.right.and.arrow.up.left")
                            } else {
                                Label("Collapse All", systemImage: "arrow.up.left.and.arrow.down.right")
                            }
                        }
                    }

                    Divider()

                    Button(role: .destructive) {
                        shoppingList.clearChecked()
                    } label: {
                        Label("Clear Checked", systemImage: "trash")
                    }
                    .disabled(shoppingList.items.filter(\.isChecked).isEmpty)

                    Button(role: .destructive) {
                        shoppingList.clearAll()
                    } label: {
                        Label("Clear All", systemImage: "trash.fill")
                    }
                    .disabled(shoppingList.items.isEmpty)
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .overlay {
            if shoppingList.items.isEmpty {
                ContentUnavailableView(
                    "No Items Yet",
                    systemImage: "cart",
                    description: Text("Select recipes and add ingredients to build your shopping list.")
                )
            } else if shoppingList.visibleItems.isEmpty {
                ContentUnavailableView(
                    "All Done!",
                    systemImage: "checkmark.circle",
                    description: Text("All items are checked off. Use the menu to show checked items or clear the list.")
                )
            }
        }
        .onAppear {
            scanForConfigs()
        }
    }

    private func toggleSection(_ name: String) {
        if collapsedSections.contains(name) {
            collapsedSections.remove(name)
        } else {
            collapsedSections.insert(name)
        }
    }

    private func toggleAllSections() {
        if allCollapsed {
            collapsedSections.removeAll()
        } else {
            collapsedSections = Set(allSectionNames)
        }
    }

    private func shoppingListItemRow(_ item: ShoppingListItem) -> some View {
        Button {
            withAnimation {
                shoppingList.toggleItem(item)
            }
        } label: {
            HStack {
                Image(systemName: item.isChecked ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(item.isChecked ? .green : .secondary)
                    .imageScale(.large)

                VStack(alignment: .leading, spacing: 2) {
                    Text(item.name)
                        .strikethrough(item.isChecked)
                        .foregroundStyle(item.isChecked ? .secondary : .primary)

                    if !item.formattedQuantities.isEmpty {
                        Text(item.formattedQuantities)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .strikethrough(item.isChecked)
                    }
                }
            }
        }
    }

    private func scanForConfigs() {
        guard let url = cookbookURL else { return }

        let accessing = url.startAccessingSecurityScopedResource()
        defer {
            if accessing { url.stopAccessingSecurityScopedResource() }
        }

        guard let enumerator = FileManager.default.enumerator(
            at: url,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        ) else { return }

        var configs: [(name: String, url: URL)] = []
        for case let fileURL as URL in enumerator {
            if fileURL.pathExtension == "toml" {
                let name = fileURL.deletingPathExtension().lastPathComponent
                configs.append((name: name, url: fileURL))
            }
        }

        availableConfigs = configs.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private func loadConfig(_ configEntry: (name: String, url: URL)) {
        guard let url = cookbookURL else { return }

        let accessing = url.startAccessingSecurityScopedResource()
        defer {
            if accessing { url.stopAccessingSecurityScopedResource() }
        }

        guard let config = try? ShoppingListConfig(contentsOf: configEntry.url) else { return }
        shoppingList.applyConfig(config)
        activeConfigName = configEntry.name
        collapsedSections.removeAll()
    }
}
