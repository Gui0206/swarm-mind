"""
API route module
"""

from flask import Blueprint

game_bp = Blueprint('game', __name__)

from . import game  # noqa: E402, F401
