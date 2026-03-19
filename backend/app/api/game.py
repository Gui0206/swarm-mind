"""
SWARM MIND — Game API Routes
"""

from flask import request, jsonify
from openai import APIStatusError
from . import game_bp
from ..services.game_engine import get_engine
from ..utils.llm_client import LLMClient
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.game.api')


def _get_locale():
    """Extract locale from Accept-Language header."""
    lang = request.headers.get('Accept-Language', 'en')
    # Parse first language tag (e.g. "pt-BR,pt;q=0.9,en;q=0.8" → "pt-BR")
    return lang.split(',')[0].strip()


def _get_llm_override():
    """Build an LLM client from the user's BYOK key, or None to use server key."""
    user_key = request.headers.get('X-User-LLM-Key')
    if user_key:
        return LLMClient(
            api_key=user_key,
            base_url='https://openrouter.ai/api/v1',
        )
    if Config.SERVER_KEY_DISABLED:
        return None  # caller must handle this
    return None


@game_bp.route('/scenarios', methods=['GET'])
def list_scenarios():
    """List available game scenarios."""
    engine = get_engine()
    locale = _get_locale()
    return jsonify(engine.get_scenarios(locale=locale))


@game_bp.route('/new', methods=['POST'])
def new_game():
    """Start a new game session."""
    try:
        data = request.get_json(silent=True) or {}
        engine = get_engine()
        locale = _get_locale()
        session = engine.new_game(data.get('scenario_id'), locale=locale)
        return jsonify(session.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create game: {e}")
        return jsonify({'error': f'Failed to create game: {str(e)}'}), 500


@game_bp.route('/new-custom', methods=['POST'])
def new_custom_game():
    """Start a game with a user-provided custom scenario."""
    try:
        data = request.get_json(silent=True) or {}
        engine = get_engine()
        session = engine.new_custom_game(data)
        return jsonify(session.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create custom game: {e}")
        return jsonify({'error': f'Failed to create custom game: {str(e)}'}), 500


@game_bp.route('/<game_id>', methods=['GET'])
def get_game(game_id):
    """Get current game state."""
    engine = get_engine()
    session = engine.get_session(game_id)
    if not session:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(session.to_dict())


@game_bp.route('/<game_id>/whisper', methods=['POST'])
def whisper(game_id):
    """Send a whisper to an agent."""
    try:
        data = request.get_json()
        if not data or 'agent_id' not in data or 'message' not in data:
            return jsonify({'error': 'Missing agent_id or message'}), 400
        engine = get_engine()
        result = engine.whisper(game_id, data['agent_id'], data['message'])
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return jsonify({'error': str(e)}), 500


@game_bp.route('/<game_id>/tick', methods=['POST'])
def tick(game_id):
    """Advance the game by one round (generates agent messages)."""
    try:
        user_key = request.headers.get('X-User-LLM-Key')
        llm_override = None

        if user_key:
            llm_override = LLMClient(
                api_key=user_key,
                base_url='https://openrouter.ai/api/v1',
            )
        elif Config.SERVER_KEY_DISABLED:
            return jsonify({
                'error': 'Server quota exceeded',
                'code': 'QUOTA_EXCEEDED',
            }), 402

        engine = get_engine()
        result = engine.tick(game_id, llm_override=llm_override)
        return jsonify(result)
    except APIStatusError as e:
        if e.status_code == 402:
            logger.warning(f"LLM 402 quota exceeded: {e}")
            return jsonify({
                'error': 'Server quota exceeded',
                'code': 'QUOTA_EXCEEDED',
            }), 402
        logger.error(f"LLM API error: {e}")
        return jsonify({'error': f'Round failed: {str(e)}'}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Tick error: {e}")
        return jsonify({'error': f'Round failed: {str(e)}'}), 500
