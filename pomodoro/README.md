# pomodoro

A native macOS Pomodoro timer built with SwiftUI and Swift Package Manager.
Runs as a small always-on-top-style window with a circular progress ring,
configurable focus/break durations, and a local history of completed focus
sessions.

## Features

- Focus / short break / long break cycle, with a long break every N focus
  sessions (configurable).
- Named sessions with optional notes, recorded once a focus session ends.
- Session history panel (view, edit, delete past sessions).
- macOS notification + sound when a session completes.
- All data is stored locally — no network calls, no accounts.

## Setup

Requires Xcode / the Swift toolchain (macOS 13+).

```sh
cd pomodoro
swift build
```

## Run

During development, run straight from Swift Package Manager:

```sh
swift run
```

Or build a double-clickable `.app` bundle:

```sh
./build_app.sh
open Pomodoro.app
```

`build_app.sh` compiles a release build, assembles `Pomodoro.app`, and
ad-hoc code-signs it so Gatekeeper doesn't block a local launch.

A VS Code launch configuration (`.vscode/launch.json`) is included for
debugging via the Swift extension.

## Data storage

Session history is stored locally in JSON at
`~/Library/Application Support/Pomodoro/sessions.json` (via `SessionStore`).
Nothing is written inside the repo and nothing leaves the machine.

## Files

- `Package.swift` — SwiftPM manifest (macOS 13+, single executable target).
- `build_app.sh` — builds a release binary and packages it into `Pomodoro.app`.
- `Sources/Pomodoro/PomodoroApp.swift` — app entry point; wires up
  `SessionStore` and `TimerModel` and configures the window.
- `Sources/Pomodoro/RootView.swift` — top-level layout: timer view plus an
  optional slide-in sessions panel.
- `Sources/Pomodoro/ContentView.swift` — the main timer screen (ring,
  controls, session name/notes fields).
- `Sources/Pomodoro/TimerModel.swift` — timer state machine: countdown,
  session-type transitions, recording completed focus sessions, and
  triggering the completion notification.
- `Sources/Pomodoro/RingProgressView.swift` — circular progress indicator.
- `Sources/Pomodoro/SettingsView.swift` — steppers for focus/break durations
  and the long-break interval.
- `Sources/Pomodoro/SessionsView.swift` — session history list (view/edit/delete).
- `Sources/Pomodoro/SessionStore.swift` — loads/saves session history as JSON
  in Application Support.
- `Sources/Pomodoro/SessionRecord.swift` — session history data model.
- `Sources/Pomodoro/DurationFormat.swift` — duration formatting helper.
- `.vscode/launch.json` — Swift extension debug configurations.

## Changelog

- `2026-07-02` — Initial macOS Pomodoro app: timer with focus/break cycle,
  named sessions with notes, local session history, and completion
  notifications.
