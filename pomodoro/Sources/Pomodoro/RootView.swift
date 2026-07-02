import SwiftUI

struct RootView: View {
    @EnvironmentObject var model: TimerModel
    @EnvironmentObject var store: SessionStore
    @State private var showSessions = false

    var body: some View {
        HStack(spacing: 0) {
            ContentView(showSessions: $showSessions)

            if showSessions {
                Divider()
                SessionsView()
                    .environmentObject(store)
                    .frame(width: 400, height: 540)
                    .transition(.move(edge: .trailing).combined(with: .opacity))
            }
        }
    }
}
