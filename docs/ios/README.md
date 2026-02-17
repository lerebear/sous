# Sous for iOS

An iOS app that replicates the `sous shop` CLI command, letting you build a shopping list from a sous cookbook on your phone.

## Prerequisites

- macOS with [Xcode](https://developer.apple.com/xcode/) 16+ installed
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) (`brew install xcodegen`)
- For device deployment: an Apple ID added to Xcode (free or paid)

## Project setup

The Xcode project is generated from `project.yml` using XcodeGen. The `.xcodeproj` is gitignored and must be regenerated after cloning:

```sh
cd ios/Sous
make project
```

## Simulator

Build the app, launch the simulator, and open it automatically:

```sh
make build-sim
```

This boots an iPhone 14 simulator by default. To use a different model:

```sh
make build-sim SIM='iPhone 16'
```

To load a cookbook directory from your Mac's file system (instead of using the in-app directory picker, which only sees the simulator's sandboxed storage):

```sh
make build-sim COOKBOOK_PATH=~/Dropbox/cookbook
```

Run unit tests:

```sh
make test
```

## Device deployment

### One-time setup

1. Open **Xcode > Settings > Accounts** and add your Apple ID.
2. Note your **Personal Team ID** from the team list on that screen.
3. Connect your iPhone via USB and trust the computer when prompted.

### Deploy

From `ios/Sous/`:

```sh
make deploy TEAM=<your-team-id>
```

This generates the Xcode project, builds a signed `.app`, and installs it on your connected iPhone in one step.

If you only need to build without installing:

```sh
make build-device TEAM=<your-team-id>
```

Or install a previously built app:

```sh
make install
```

### Free Apple ID limitations

Apps signed with a free Apple ID expire after 7 days. Re-run `make deploy` to refresh.

## All make targets

| Target | Description |
|--------|-------------|
| `make project` | Regenerate Xcode project from `project.yml` |
| `make build-sim` | Build and launch in simulator |
| `make test` | Run unit tests on simulator |
| `make build-device TEAM=...` | Build signed `.app` for a physical device |
| `make install` | Install previously built app onto connected iPhone |
| `make deploy TEAM=...` | Build + install in one step |
| `make clean` | Remove build artifacts |
| `make help` | Print usage summary |
