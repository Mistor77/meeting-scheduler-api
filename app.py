from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_score(local_hour):
    if 7 <= local_hour <= 20:
        return 0
    elif local_hour == 21:
        return 1
    return None

def find_best_meeting_time(members):
    favored = list(range(7, 22))  # 7 AM to 9 PM
    candidates = []
    for u in range(24):
        valid = True
        total_score = 0
        details = {}
        for member in members:
            name = member['name']
            offset = float(member['offset'])
            local_hour = (u + offset) % 24
            if local_hour not in favored:
                valid = False
                break
            score = get_score(local_hour)
            if score is None:
                valid = False
                break
            total_score += score
            hour = int(local_hour)
            minutes = int((local_hour % 1) * 60)
            am_pm = "AM" if hour < 12 else "PM"
            display_h = hour % 12 if hour % 12 != 0 else 12
            display_time = f"{display_h}:{minutes:02d} {am_pm}"
            details[name] = {'local_time': display_time, 'score': score}
        if valid:
            candidates.append((total_score, u, details))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0]

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    members = data.get('members', [])
    result = find_best_meeting_time(members)
    if result is None:
        return jsonify({'error': 'No valid time found'}), 400
    total_score, utc_hour, details = result
    return jsonify({
        'best_utc': utc_hour,
        'total_score': total_score,
        'details': details
    })

if __name__ == '__main__':
    app.run()
