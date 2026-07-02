import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var model: TimerModel

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Durations (minutes)")
                .font(.headline)

            Stepper("Focus: \(model.workMinutes)", value: $model.workMinutes, in: 1...90)
            Stepper("Short break: \(model.shortBreakMinutes)", value: $model.shortBreakMinutes, in: 1...30)
            Stepper("Long break: \(model.longBreakMinutes)", value: $model.longBreakMinutes, in: 1...60)
            Stepper("Long break after: \(model.longBreakInterval) sessions", value: $model.longBreakInterval, in: 1...8)
        }
        .padding(20)
        .frame(width: 280)
    }
}
