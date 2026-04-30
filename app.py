import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from db import init_db, get_db
from handlers import users_handler, admin_handler, ai_handler

# Auto-load .env
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ[_k.strip()] = _v.strip()

app = Flask(__name__, static_folder='.', static_url_path='')

init_db()

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online", "message": "FRES Backend active!", "version": "2.0.0"})

@app.route('/api/users/login', methods=['POST'])
def login():
    return users_handler.login_handler(request)

@app.route('/api/users/register', methods=['POST'])
def register():
    return users_handler.register_handler(request)

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    return admin_handler.stats_handler(request)

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    return admin_handler.get_users_handler(request)

@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    return admin_handler.update_user_status_handler(request, user_id)

@app.route('/api/admin/suggestions', methods=['GET'])
def get_suggestions():
    return admin_handler.get_suggestions_handler(request)

@app.route('/api/admin/suggestions/<int:suggestion_id>/reply', methods=['POST'])
def reply_suggestion(suggestion_id):
    return admin_handler.reply_suggestion_handler(request, suggestion_id)

@app.route('/api/admin/announcements', methods=['GET', 'POST'])
def announcements():
    if request.method == 'GET':
        return admin_handler.get_announcements_handler(request)
    return admin_handler.post_announcement_handler(request)

@app.route('/api/ai/generate', methods=['POST'])
def generate():
    return ai_handler.generate_handler(request)

@app.route('/api/ai/logs', methods=['GET'])
def get_logs():
    return ai_handler.get_logs_handler(request)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
