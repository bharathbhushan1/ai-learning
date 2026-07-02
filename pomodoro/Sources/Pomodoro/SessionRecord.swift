import Foundation

struct SessionRecord: Identifiable, Codable, Equatable {
    let id: UUID
    var name: String
    var type: SessionType
    var startDate: Date
    var endDate: Date
    var plannedSeconds: Int
    var notes: String
    var completed: Bool

    init(id: UUID, name: String, type: SessionType, startDate: Date, endDate: Date, plannedSeconds: Int, notes: String = "", completed: Bool = true) {
        self.id = id
        self.name = name
        self.type = type
        self.startDate = startDate
        self.endDate = endDate
        self.plannedSeconds = plannedSeconds
        self.notes = notes
        self.completed = completed
    }

    private enum CodingKeys: String, CodingKey {
        case id, name, type, startDate, endDate, plannedSeconds, notes, completed
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        name = try c.decode(String.self, forKey: .name)
        type = try c.decode(SessionType.self, forKey: .type)
        startDate = try c.decode(Date.self, forKey: .startDate)
        endDate = try c.decode(Date.self, forKey: .endDate)
        plannedSeconds = try c.decode(Int.self, forKey: .plannedSeconds)
        notes = try c.decodeIfPresent(String.self, forKey: .notes) ?? ""
        completed = try c.decodeIfPresent(Bool.self, forKey: .completed) ?? true
    }

    var actualSeconds: Int {
        max(0, Int(endDate.timeIntervalSince(startDate)))
    }

    var displayName: String {
        name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? type.rawValue : name
    }
}
