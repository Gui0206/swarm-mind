"""
BYOK Auth — OpenRouter OAuth code exchange proxy
"""

import json
import urllib.request
import urllib.error
from flask import request, jsonify
from . import auth_bp
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger('mirofish.auth')

OPENROUTER_EXCHANGE_URL = 'https://openrouter.ai/api/v1/auth/keys'


@auth_bp.route('/exchange', methods=['POST'])
def exchange_code():
    """Exchange an OpenRouter auth code for an API key."""
    data = request.get_json(silent=True) or {}
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Missing auth code'}), 400

    try:
        payload = json.dumps({'code': code}).encode('utf-8')
        req = urllib.request.Request(
            OPENROUTER_EXCHANGE_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        key = result.get('key')
        if not key:
            return jsonify({'error': 'No key returned from OpenRouter'}), 502

        logger.info('BYOK: user key exchanged successfully')
        return jsonify({'key': key})

    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        logger.error(f'OpenRouter exchange failed ({e.code}): {body}')
        return jsonify({'error': 'OpenRouter auth failed'}), 502
    except Exception as e:
        logger.error(f'Exchange error: {e}')
        return jsonify({'error': 'Auth exchange failed'}), 500


@auth_bp.route('/status', methods=['GET'])
def server_status():
    """Check if the server key is active."""
    return jsonify({
        'server_key_active': not Config.SERVER_KEY_DISABLED and bool(Config.LLM_API_KEY),
    })
