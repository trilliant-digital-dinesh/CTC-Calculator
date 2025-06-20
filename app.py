import json
from collections import defaultdict

# Load your JSON input (replace with actual data source if needed)
with open("import.json", "r") as f:
    data = json.load(f)

# Fields to sum
int_fields = ["sessions", "newUsers", "engagedSessions", "eventCount", "totalUsers"]
float_fields = ["engagementRate", "averageSessionDuration", "sessionsPerUser", "eventCountPerUser"]

# Initialize aggregation dictionary
grouped = defaultdict(lambda: {k: 0 for k in int_fields + float_fields})

# Helper function to safely convert to number
def to_float(val): return float(val) if val != "" else 0.0
def to_int(val): return int(float(val)) if val != "" else 0

# Group and sum
for row in data:
    group = row.get("sessionDefaultChannelGroup", "Unassigned")
    for field in int_fields:
        grouped[group][field] += to_int(row.get(field, 0))
    grouped[group]["engagementRate"] += to_float(row.get("engagementRate", 0)) * to_int(row.get("sessions", 0))
    grouped[group]["averageSessionDuration"] += to_float(row.get("averageSessionDuration", 0)) * to_int(row.get("sessions", 0))

# Prepare final result list
result = []

for group, metrics in grouped.items():
    sessions = metrics["sessions"]
    total_users = metrics["totalUsers"]

    result.append({
        "sessionDefaultChannelGroup": group,
        "sessions": sessions,
        "newUsers": metrics["newUsers"],
        "engagedSessions": metrics["engagedSessions"],
        "engagementRate": metrics["engagementRate"] / sessions if sessions else 0,
        "averageSessionDuration": metrics["averageSessionDuration"] / sessions if sessions else 0,
        "eventCount": metrics["eventCount"],
        "totalUsers": total_users,
        "sessionsPerUser": sessions / total_users if total_users else 0,
        "eventCountPerUser": metrics["eventCount"] / total_users if total_users else 0,
    })

# Add total row
total = defaultdict(float)
for row in result:
    for key in int_fields:
        total[key] += row[key]
    total["engagementRate"] += row["engagementRate"] * row["sessions"]
    total["averageSessionDuration"] += row["averageSessionDuration"] * row["sessions"]

total_sessions = total["sessions"]
total_users = total["totalUsers"]

total_row = {
    "sessionDefaultChannelGroup": "Total",
    "sessions": int(total["sessions"]),
    "newUsers": int(total["newUsers"]),
    "engagedSessions": int(total["engagedSessions"]),
    "engagementRate": total["engagementRate"] / total_sessions if total_sessions else 0,
    "averageSessionDuration": total["averageSessionDuration"] / total_sessions if total_sessions else 0,
    "eventCount": int(total["eventCount"]),
    "totalUsers": int(total_users),
    "sessionsPerUser": total["sessions"] / total_users if total_users else 0,
    "eventCountPerUser": total["eventCount"] / total_users if total_users else 0,
}

# Final output
final_output = [total_row] + sorted(result, key=lambda x: x["sessionDefaultChannelGroup"])

# Save or print
print(json.dumps(final_output, indent=2))