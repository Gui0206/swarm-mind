"""
Vercel Serverless Entry Point
Wraps the Flask app for Vercel's Python runtime.
"""

import sys
import os

# Add backend to Python path so `from app import ...` works
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)

from app import create_app

app = create_app()
