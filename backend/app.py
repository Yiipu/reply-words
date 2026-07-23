import os
import sys
import hashlib
import re
import json
from flask import Flask, request, jsonify, send_from_directory, abort

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import (
    get_community_words, add_word, add_feedback, word_exists,
    run_fade_out, COMMUNITY_JSON
)

app = Flask(__name__, static_folder=None)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# ── Hard constraints ──
MAX_WORD_LENGTH = 100
VALID_CHARS = re.compile(
    r'^[\u4e00-\u9fff\u3000-\u303f\uff00-\uffefa-zA-Z0-9\s,./;'
    r'\'!?@#$%^&*()_+\-=[\]{}|:"<>?~`]+$'
)


def validate_hard(word, category, mode):
    """Return (ok, error_message)."""
    if not word or not isinstance(word, str):
        return False, "内容不能为空"
    word = word.strip()
    if len(word) > MAX_WORD_LENGTH:
        return False, f"词条长度不能超过{MAX_WORD_LENGTH}个字符"
    if len(word) < 1:
        return False, "内容不能为空"
    if not VALID_CHARS.match(word):
        return False, "词条包含不支持的字符"
    if category not in ('leader', 'colleague'):
        return False, "类别无效"
    if mode not in ('ok', 'no'):
        return False, "模式无效"
    if word_exists(word, category, mode):
        return False, "该词条已存在"
    return True, None


# ── PAW check placeholder ──
def paw_check(word, category, mode):
    """
    PAW (Program as Weight) semantic validation.
    Returns (passed, reason).
    Currently a stub — will be replaced once PAW skill is installed.
    """
    # TODO: integrate with programasweights.com PAW
    return True, None


# ── Routes ──

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    if '..' in filename or filename.startswith('/'):
        abort(404)
    return send_from_directory(STATIC_DIR, filename)


@app.route('/api/community-words')
def community_words():
    """Return community words with ETag for caching."""
    try:
        mtime = os.path.getmtime(COMMUNITY_JSON)
    except OSError:
        return jsonify({
            "ok": {"leader": [], "colleague": []},
            "no": {"leader": [], "colleague": []}
        })

    etag = f'"{hashlib.md5(str(mtime).encode()).hexdigest()}"'

    if request.headers.get('If-None-Match') == etag:
        return '', 304

    with open(COMMUNITY_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    resp = jsonify(data)
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'public, max-age=60'
    return resp


@app.route('/api/submit', methods=['POST'])
def submit():
    """Submit a word. Runs hard constraints, then PAW, then stores."""
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "请提供JSON格式的投稿"}), 400

    word = (body.get('text') or '').strip()
    category = body.get('category', '')
    mode = body.get('mode', '')

    # Hard constraints
    ok, err = validate_hard(word, category, mode)
    if not ok:
        return jsonify({"error": err}), 400

    # PAW semantic check
    paw_ok, paw_reason = paw_check(word, category, mode)
    if not paw_ok:
        return jsonify({"error": paw_reason or "审核未通过"}), 400

    # Store
    word_id = add_word(word, category, mode)
    return jsonify({"id": word_id, "text": word, "status": "accepted"}), 201


@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Record feedback (vote: 1 for like, -1 for dislike)."""
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "请提供JSON格式的反馈"}), 400

    word_id = body.get('word_id')
    vote = body.get('vote')

    if not isinstance(word_id, int) or word_id <= 0:
        return jsonify({"error": "无效的词条ID"}), 400
    if vote not in (1, -1):
        return jsonify({"error": "vote 必须为 1 或 -1"}), 400

    add_feedback(word_id, vote)
    return jsonify({"status": "recorded"}), 200


@app.route('/api/fade-out', methods=['POST'])
def trigger_fade_out():
    """Admin trigger for fade-out (also runs periodically)."""
    faded = run_fade_out()
    return jsonify({"faded": faded})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8799, debug=False)
