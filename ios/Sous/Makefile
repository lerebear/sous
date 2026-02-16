PROJECT = Sous.xcodeproj
SCHEME  = Sous
BUNDLE  = com.lerebear.Sous

# Generate the Xcode project from project.yml (requires xcodegen)
.PHONY: project
project:
	xcodegen generate

# Simulator device name (override with SIM=... if needed)
SIM ?= iPhone 14

# Build for the iOS Simulator and launch the app
.PHONY: build-sim
build-sim: project
	xcodebuild build \
		-project $(PROJECT) -scheme $(SCHEME) \
		-destination 'platform=iOS Simulator,name=$(SIM)' \
		CODE_SIGN_IDENTITY=- CODE_SIGNING_REQUIRED=NO \
		| grep -E '^(Compiling|Linking|Build |error:|\*\*)' || true
	@echo ""
	@echo "Launching simulator..."
	xcrun simctl boot '$(SIM)' 2>/dev/null || true
	open -a Simulator
	xcrun simctl install '$(SIM)' $$(xcodebuild -project $(PROJECT) -scheme $(SCHEME) \
		-destination 'platform=iOS Simulator,name=$(SIM)' \
		-showBuildSettings 2>/dev/null \
		| grep -m1 BUILT_PRODUCTS_DIR | awk '{print $$3}')/Sous.app
	xcrun simctl launch '$(SIM)' $(BUNDLE)

# Run unit tests on the simulator
.PHONY: test
test: project
	xcodebuild test \
		-project $(PROJECT) -scheme $(SCHEME) \
		-destination 'platform=iOS Simulator,name=$(SIM)' \
		CODE_SIGN_IDENTITY=- CODE_SIGNING_REQUIRED=NO \
		| grep -E '^(Test |error:|\*\*)' || true

# ---------- Physical device deployment ----------

# Discover the first connected iPhone's UDID
DEVICE_UDID = $(shell xcrun devicectl list devices 2>/dev/null \
	| grep -i iphone | head -1 | awk '{print $$NF}')

# Build directory for device builds
BUILD_DIR = build

# Build a signed .app for a physical device.
# Requires: Apple ID added to Xcode (Settings > Accounts), DEVELOPMENT_TEAM set.
#
# On first use, pass your team ID:
#   make build-device TEAM=<YOUR_TEAM_ID>
#
# Find your team ID: open Xcode > Settings > Accounts > select your Apple ID >
# look for your "Personal Team" row and note the Team ID.
TEAM ?=

.PHONY: build-device
build-device: project
	$(if $(TEAM),,$(error Set TEAM to your Apple Developer Team ID, e.g. make build-device TEAM=ABCDE12345))
	xcodebuild build \
		-project $(PROJECT) -scheme $(SCHEME) \
		-destination 'generic/platform=iOS' \
		-derivedDataPath $(BUILD_DIR) \
		DEVELOPMENT_TEAM=$(TEAM) \
		CODE_SIGN_STYLE=Automatic \
		CODE_SIGN_IDENTITY="Apple Development" \
		| grep -E '^(Compiling|Linking|Build |Signing|error:|\*\*)' || true
	@echo ""
	@echo "Built: $(BUILD_DIR)/Build/Products/Debug-iphoneos/Sous.app"

# Install the built app onto a connected iPhone.
.PHONY: install
install:
	$(if $(DEVICE_UDID),,$(error No iPhone detected. Connect your phone via USB and trust this computer.))
	@echo "Installing to device $(DEVICE_UDID)..."
	xcrun devicectl device install app \
		--device $(DEVICE_UDID) \
		$(BUILD_DIR)/Build/Products/Debug-iphoneos/Sous.app

# One command: build + install onto connected iPhone.
#   make deploy TEAM=<YOUR_TEAM_ID>
.PHONY: deploy
deploy: build-device install
	@echo ""
	@echo "Sous deployed to your iPhone! Open the app to get started."
	@echo ""
	@echo "Note: Free Apple ID apps expire after 7 days."
	@echo "Just run 'make deploy TEAM=$(TEAM)' again to refresh."

# Clean build artifacts
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	xcodebuild clean -project $(PROJECT) -scheme $(SCHEME) 2>/dev/null || true

.PHONY: help
help:
	@echo "Sous iOS App"
	@echo ""
	@echo "Simulator:"
	@echo "  make build-sim     Build and launch in simulator"
	@echo "  make test          Run unit tests on simulator"
	@echo "  (override simulator with SIM='iPhone 16', etc.)"
	@echo ""
	@echo "Device (requires USB + Apple ID in Xcode):"
	@echo "  make deploy TEAM=ABCDE12345   Build and install on connected iPhone"
	@echo "  make build-device TEAM=...    Build only"
	@echo "  make install                  Install previously built app"
	@echo ""
	@echo "Other:"
	@echo "  make project       Regenerate Xcode project"
	@echo "  make clean         Clean build artifacts"
	@echo ""
	@echo "First-time setup:"
	@echo "  1. Open Xcode > Settings > Accounts > add your Apple ID"
	@echo "  2. Note your Personal Team ID from that screen"
	@echo "  3. Connect iPhone via USB, trust computer"
	@echo "  4. make deploy TEAM=<your-team-id>"
