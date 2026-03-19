"""
Configuration — loads from project root .env
"""

import os
from dotenv import load_dotenv

project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    load_dotenv(override=True)


class Config:
    """Flask configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'swarmmind-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    JSON_AS_ASCII = False

    # LLM (OpenAI-compatible)
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')

    # BYOK: if True, the server key is disabled and users must provide their own
    SERVER_KEY_DISABLED = os.environ.get('SERVER_KEY_DISABLED', 'false').lower() == 'true'

    @classmethod
    def validate(cls):
        """Validate required config."""
        errors = []
        if not cls.LLM_API_KEY and not cls.SERVER_KEY_DISABLED:
            errors.append("LLM_API_KEY is not configured")
        return errors
