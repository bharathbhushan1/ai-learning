import Foundation
import AppKit
import UserNotifications
import Combine

enum SessionType: String, CaseIterable, Codable {
    case work = "Focus"
    case shortBreak = "Short Break"
    case longBreak = "Long Break"

    var accent: (Double, Double, Double) {
        switch self {
        case .work: return (0.20, 0.68, 0.38)        // green
        case .shortBreak: return (0.95, 0.62, 0.15)  // amber
        case .longBreak: return (0.45, 0.40, 0.90)   // indigo
        }
    }
}

final class TimerModel: ObservableObject {
    // Configurable durations (in minutes)
    @Published var workMinutes: Int = 25 { didSet { if sessionType == .work && !isRunning { resetClockForCurrentSession() } } }
    @Published var shortBreakMinutes: Int = 5 { didSet { if sessionType == .shortBreak && !isRunning { resetClockForCurrentSession() } } }
    @Published var longBreakMinutes: Int = 15 { didSet { if sessionType == .longBreak && !isRunning { resetClockForCurrentSession() } } }
    @Published var longBreakInterval: Int = 4

    @Published private(set) var secondsRemaining: Int
    @Published private(set) var isRunning: Bool = false
    @Published private(set) var sessionType: SessionType = .work
    @Published private(set) var completedPomodoros: Int = 0
    @Published var currentSessionName: String = ""
    @Published var currentSessionNote: String = ""

    private var timer: Timer?
    private var sessionStartDate: Date = Date()
    private let store: SessionStore

    init(store: SessionStore) {
        self.store = store
        secondsRemaining = 25 * 60
        requestNotificationPermission()
    }

    var totalSeconds: Int {
        switch sessionType {
        case .work: return workMinutes * 60
        case .shortBreak: return shortBreakMinutes * 60
        case .longBreak: return longBreakMinutes * 60
        }
    }

    var progress: Double {
        guard totalSeconds > 0 else { return 0 }
        return 1.0 - (Double(secondsRemaining) / Double(totalSeconds))
    }

    var formattedTime: String {
        let m = secondsRemaining / 60
        let s = secondsRemaining % 60
        return String(format: "%02d:%02d", m, s)
    }

    func start() {
        guard !isRunning else { return }
        isRunning = true
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    func pause() {
        isRunning = false
        timer?.invalidate()
        timer = nil
    }

    func toggle() {
        isRunning ? pause() : start()
    }

    func reset() {
        pause()
        resetClockForCurrentSession()
    }

    func skip() {
        advanceSession(completedNaturally: false)
    }

    private func resetClockForCurrentSession() {
        secondsRemaining = totalSeconds
        sessionStartDate = Date()
    }

    private func tick() {
        guard secondsRemaining > 0 else {
            advanceSession(completedNaturally: true)
            return
        }
        secondsRemaining -= 1
    }

    private func advanceSession(completedNaturally: Bool) {
        pause()

        let endedType = sessionType
        let endedName = currentSessionName.trimmingCharacters(in: .whitespacesAndNewlines)
        let endedPlannedSeconds = totalSeconds
        let endedActualSeconds = max(0, Int(Date().timeIntervalSince(sessionStartDate)))

        if endedType == .work {
            let record = SessionRecord(
                id: UUID(),
                name: currentSessionName,
                type: endedType,
                startDate: sessionStartDate,
                endDate: Date(),
                plannedSeconds: endedPlannedSeconds,
                notes: currentSessionNote,
                completed: completedNaturally
            )
            if record.actualSeconds > 0 {
                store.add(record)
            }
        }

        if completedNaturally {
            notifySessionEnded(
                type: endedType,
                name: endedName,
                plannedSeconds: endedPlannedSeconds,
                actualSeconds: endedActualSeconds
            )
        }

        switch sessionType {
        case .work:
            completedPomodoros += 1
            sessionType = (completedPomodoros % longBreakInterval == 0) ? .longBreak : .shortBreak
        case .shortBreak, .longBreak:
            sessionType = .work
        }

        currentSessionName = ""
        currentSessionNote = ""
        resetClockForCurrentSession()

        if completedNaturally {
            start()
        }
    }

    private func notifySessionEnded(type: SessionType, name: String, plannedSeconds: Int, actualSeconds: Int) {
        NSSound(named: "Glass")?.play()
        NSApp.requestUserAttention(.informationalRequest)

        let content = UNMutableNotificationContent()
        switch type {
        case .work:
            content.title = "Focus session complete"
        case .shortBreak:
            content.title = "Short break complete"
        case .longBreak:
            content.title = "Long break complete"
        }

        if !name.isEmpty {
            content.subtitle = name
        }
        content.body = "Planned \(formatDuration(plannedSeconds)) · Actual \(formatDuration(actualSeconds))"
        content.sound = .default

        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }

    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }
}
