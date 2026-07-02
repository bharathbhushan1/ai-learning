import SwiftUI

struct SessionsView: View {
    @EnvironmentObject var store: SessionStore
    @State private var searchText = ""

    private var filteredRecords: [SessionRecord] {
        guard !searchText.trimmingCharacters(in: .whitespaces).isEmpty else { return store.records }
        return store.records.filter {
            $0.displayName.localizedCaseInsensitiveContains(searchText) ||
            $0.type.rawValue.localizedCaseInsensitiveContains(searchText) ||
            $0.notes.localizedCaseInsensitiveContains(searchText)
        }
    }

    private var groupedByDay: [(day: Date, records: [SessionRecord])] {
        let calendar = Calendar.current
        let groups = Dictionary(grouping: filteredRecords) { calendar.startOfDay(for: $0.startDate) }
        return groups.keys.sorted(by: >).map { day in
            (day, groups[day]!.sorted { $0.startDate > $1.startDate })
        }
    }

    private func binding(for record: SessionRecord) -> Binding<SessionRecord> {
        Binding(
            get: { store.records.first(where: { $0.id == record.id }) ?? record },
            set: { store.update($0) }
        )
    }

    var body: some View {
        VStack(spacing: 0) {
            Text("Sessions")
                .font(.system(size: 18, weight: .bold))
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16)
                .padding(.top, 16)
                .padding(.bottom, 10)

            HStack(spacing: 6) {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(.secondary)
                TextField("Search sessions", text: $searchText)
                    .textFieldStyle(.plain)
                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .font(.system(size: 13))
            .padding(.horizontal, 8)
            .padding(.vertical, 6)
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 8))
            .padding(.horizontal, 16)
            .padding(.bottom, 10)

            Divider()

            Group {
                if filteredRecords.isEmpty {
                    emptyState
                } else {
                    List {
                        ForEach(groupedByDay, id: \.day) { group in
                            Section {
                                ForEach(group.records) { record in
                                    SessionRow(record: binding(for: record)) {
                                        store.delete(record)
                                    }
                                }
                            } header: {
                                DaySummaryHeader(day: group.day, records: group.records, label: dayLabel(group.day))
                            }
                        }
                    }
                    .listStyle(.inset)
                }
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 10) {
            Image(systemName: "tray")
                .font(.system(size: 34))
                .foregroundStyle(.secondary)
            Text(searchText.isEmpty ? "No sessions yet" : "No matching sessions")
                .font(.headline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func dayLabel(_ date: Date) -> String {
        if Calendar.current.isDateInToday(date) { return "Today" }
        if Calendar.current.isDateInYesterday(date) { return "Yesterday" }
        let formatter = DateFormatter()
        formatter.dateStyle = .full
        return formatter.string(from: date)
    }
}

private struct DaySummaryHeader: View {
    let day: Date
    let records: [SessionRecord]
    let label: String

    private var completedCount: Int { records.filter { $0.completed }.count }
    private var skippedCount: Int { records.count - completedCount }
    private var focusedSeconds: Int { records.reduce(0) { $0 + $1.actualSeconds } }
    private var plannedSeconds: Int { records.reduce(0) { $0 + $1.plannedSeconds } }

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(label)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(.primary)
                Spacer()
                Text("\(formatDuration(focusedSeconds)) focused")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            HStack(spacing: 10) {
                statLabel("\(records.count) session\(records.count == 1 ? "" : "s")", icon: "list.bullet")
                statLabel("\(completedCount) completed", icon: "checkmark.circle")
                if skippedCount > 0 {
                    statLabel("\(skippedCount) skipped", icon: "forward.end")
                }
                statLabel("planned \(formatDuration(plannedSeconds))", icon: "hourglass")
            }
        }
        .padding(.vertical, 4)
        .textCase(nil)
    }

    private func statLabel(_ text: String, icon: String) -> some View {
        Label(text, systemImage: icon)
            .font(.caption2)
            .foregroundStyle(.secondary)
            .labelStyle(.titleAndIcon)
    }
}

private struct SessionRow: View {
    @Binding var record: SessionRecord
    let onDelete: () -> Void

    @State private var isHovering = false

    private var accent: Color {
        let (r, g, b) = record.type.accent
        return Color(red: r, green: g, blue: b)
    }

    private var timeRangeText: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .none
        formatter.timeStyle = .short
        return "\(formatter.string(from: record.startDate)) – \(formatter.string(from: record.endDate))"
    }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Circle()
                .fill(accent)
                .frame(width: 10, height: 10)
                .padding(.top, 5)

            VStack(alignment: .leading, spacing: 3) {
                TextField(record.type.rawValue, text: $record.name)
                    .textFieldStyle(.plain)
                    .font(.system(size: 14, weight: .semibold))

                HStack(spacing: 6) {
                    Text(record.type.rawValue)
                        .font(.caption)
                        .foregroundStyle(accent)
                    Text("·")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text("planned \(formatDuration(record.plannedSeconds))")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    if !record.completed {
                        Text("·")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text("skipped")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                }

                HStack(spacing: 5) {
                    Image(systemName: "text.bubble")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    TextField("Add a note…", text: $record.notes)
                        .textFieldStyle(.plain)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding(.top, 2)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 3) {
                Text(timeRangeText)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(formatDuration(record.actualSeconds))
                    .font(.system(size: 12, weight: .medium))
            }

            Button(action: onDelete) {
                Image(systemName: "trash")
                    .font(.system(size: 12))
                    .foregroundStyle(isHovering ? Color.red : Color.secondary.opacity(0.35))
                    .frame(width: 20, height: 20)
                    .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .help("Delete this session")
            .onHover { isHovering = $0 }
        }
        .padding(.vertical, 5)
    }
}
