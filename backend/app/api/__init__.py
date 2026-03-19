"""
API route module
"""

from flask import Blueprint

game_bp = Blueprint('game', __name__)
auth_bp = Blueprint('auth', __name__)

from . import game  # noqa: E402, F401
from . import auth  # noqa: E402, F401
