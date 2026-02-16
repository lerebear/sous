import SwiftUI
import UIKit

struct DirectoryPicker: UIViewControllerRepresentable {
    var onPick: (URL) -> Void

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.folder])
        picker.allowsMultipleSelection = false
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(onPick: onPick)
    }

    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        let onPick: (URL) -> Void

        init(onPick: @escaping (URL) -> Void) {
            self.onPick = onPick
        }

        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }
            onPick(url)
        }
    }
}

struct CookbookPickerView: View {
    @Bindable var cookbook: CookbookViewModel

    var body: some View {
        VStack(spacing: 32) {
            Spacer()

            VStack(spacing: 12) {
                Image(systemName: "book.closed")
                    .font(.system(size: 60))
                    .foregroundStyle(.secondary)

                Text("Sous")
                    .font(.largeTitle.bold())

                Text("Choose a cookbook directory to get started.")
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            VStack(spacing: 16) {
                Button {
                    cookbook.showDirectoryPicker = true
                } label: {
                    Label("Choose Cookbook Directory", systemImage: "folder")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)

                #if DEBUG
                Button {
                    cookbook.loadBundledRecipes()
                } label: {
                    Label("Use Sample Recipes", systemImage: "doc.text")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
                #endif
            }
            .padding(.horizontal, 32)

            if let error = cookbook.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
                    .padding(.horizontal)
            }

            Spacer()
            Spacer()
        }
        .sheet(isPresented: $cookbook.showDirectoryPicker) {
            DirectoryPicker { url in
                cookbook.loadCookbook(from: url)
            }
        }
    }
}
