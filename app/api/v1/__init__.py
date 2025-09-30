"""
API v1 module for RCM SaaS Application
"""

from flask import Blueprint
from .routes import v1_bp

__all__ = ['v1_bp']
