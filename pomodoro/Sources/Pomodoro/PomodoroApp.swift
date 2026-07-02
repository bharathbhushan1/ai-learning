import SwiftUI

@main
struct PomodoroApp: App {
    @StateObject private var store: SessionStore
    @StateObject private var model: TimerModel

    init() {
        let store = SessionStore()
        _store = StateObject(wrappedValue: store)
        _model = StateObject(wrappedValue: TimerModel(store: store))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .environmentObject(store)
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)
        .defaultPosition(.center)
        .commands {
            CommandGroup(replacing: .newItem) { }
        }
    }
}
