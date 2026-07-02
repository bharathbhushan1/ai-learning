import SwiftUI

struct ContentView: View {
    @EnvironmentObject var model: TimerModel
    @Binding var showSessions: Bool
    @State private var showSettings = false

    private var accent: Color {
        let (r, g, b) = model.sessionType.accent
        return Color(red: r, green: g, blue: b)
    }

    var body: some View {
        ZStack {
            accent.opacity(0.08).ignoresSafeArea()

            VStack(spacing: 28) {
                HStack {
                    Text(model.sessionType.rawValue)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(accent)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 5)
                        .background(accent.opacity(0.15), in: Capsule())

                    Spacer()

                    Button {
                        withAnimation(.easeInOut(duration: 0.25)) {
                            showSessions.toggle()
                        }
                    } label: {
                        Image(systemName: "sidebar.right")
                            .foregroundStyle(showSessions ? accent : .secondary)
                    }
                    .buttonStyle(.plain)
                    .help(showSessions ? "Hide sessions" : "Show sessions")

                    Button {
                        showSettings.toggle()
                    } label: {
                        Image(systemName: "gearshape.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                    .help("Timer settings")
                    .popover(isPresented: $showSettings) {
                        SettingsView()
                            .environmentObject(model)
                    }
                }
                .padding(.horizontal, 28)
                .padding(.top, 22)

                VStack(spacing: 8) {
                    TextField("Name this session", text: $model.currentSessionName)
                        .textFieldStyle(.plain)
                        .font(.system(size: 13, weight: .medium))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 7)
                        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 8))
                        .help("Give this session a name, e.g. \"Write report\"")

                    TextField("Add a note (optional)", text: $model.currentSessionNote)
                        .textFieldStyle(.plain)
                        .font(.system(size: 12))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 7)
                        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 8))
                        .help("Add notes or details about this session")
                }
                .padding(.horizontal, 28)

                ZStack {
                    RingProgressView(progress: model.progress, accent: accent)
                        .frame(width: 220, height: 220)

                    VStack(spacing: 6) {
                        Text(model.formattedTime)
                            .font(.system(size: 52, weight: .bold, design: .rounded))
                            .monospacedDigit()
                            .foregroundStyle(.primary)
                        Text(model.isRunning ? "Running" : "Paused")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                PomodoroDots(count: model.completedPomodoros, interval: model.longBreakInterval)

                HStack(spacing: 16) {
                    Button {
                        model.reset()
                    } label: {
                        Image(systemName: "arrow.counterclockwise")
                            .font(.system(size: 16, weight: .semibold))
                            .frame(width: 44, height: 44)
                            .contentShape(Circle())
                    }
                    .buttonStyle(.plain)
                    .background(.thinMaterial, in: Circle())
                    .help("Reset the current session")

                    Button {
                        model.toggle()
                    } label: {
                        Image(systemName: model.isRunning ? "pause.fill" : "play.fill")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundStyle(.white)
                            .frame(width: 72, height: 72)
                            .contentShape(Circle())
                    }
                    .buttonStyle(.plain)
                    .background(accent, in: Circle())
                    .shadow(color: accent.opacity(0.4), radius: 10, y: 4)
                    .help(model.isRunning ? "Pause" : "Start")

                    Button {
                        model.skip()
                    } label: {
                        Image(systemName: "forward.end.fill")
                            .font(.system(size: 16, weight: .semibold))
                            .frame(width: 44, height: 44)
                            .contentShape(Circle())
                    }
                    .buttonStyle(.plain)
                    .background(.thinMaterial, in: Circle())
                    .help("Skip to the next session")
                }

                Spacer(minLength: 22)
            }
        }
        .frame(width: 340, height: 540)
        .animation(.easeInOut(duration: 0.3), value: model.sessionType)
    }
}

struct PomodoroDots: View {
    let count: Int
    let interval: Int

    var body: some View {
        let filled = interval == 0 ? 0 : count % interval
        HStack(spacing: 8) {
            ForEach(0..<max(interval, 1), id: \.self) { i in
                Circle()
                    .fill(i < filled ? Color.primary : Color.primary.opacity(0.15))
                    .frame(width: 7, height: 7)
            }
        }
    }
}
