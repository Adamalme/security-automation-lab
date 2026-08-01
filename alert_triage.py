def analyze_threat(name, level):
    if level >= 9:
        return "🚨 CRITICAL"
    elif level >= 7:
        return "⚠️ HIGH"
    else:
        return "✅ LOW"

threats = [
    {"name": "Password Spray", "level": 9},
    {"name": "Guest Login", "level": 3},
    {"name": "Admin from Somalia", "level": 7},
    {"name": "MFA Bypass", "level": 10},
    {"name": "Suspicious Login", "level": 5}
]

print("=== SOC THREAT ANALYSIS ===")
for threat in threats:
    result = analyze_threat(threat["name"], threat["level"])
    print(f"{result} - {threat['name']}")
print("=== ANALYSIS COMPLETE ===")