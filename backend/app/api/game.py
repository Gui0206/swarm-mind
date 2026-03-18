"""
SWARM MIND — Game API Routes
"""

from flask import request, jsonify
from . import game_bp
from ..services.game_engine import get_engine
from ..utils.logger import get_logger

logger = get_logger('mirofish.game.api')


@game_bp.route('/scenarios', methods=['GET'])
def list_scenarios():
    """List available game scenarios."""
    engine = get_engine()
    return jsonify(engine.get_scenarios())


@game_bp.route('/new', methods=['POST'])
def new_game():
    """Start a new game session."""
    try:
        data = request.get_json(silent=True) or {}
        engine = get_engine()
        session = engine.new_game(data.get('scenario_id'))
        return jsonify(session.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create game: {e}")
        return jsonify({'error': f'Failed to create game: {str(e)}'}), 500


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
        engine = get_engine()
        result = engine.tick(game_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Tick error: {e}")
        return jsonify({'error': f'Round failed: {str(e)}'}), 500
