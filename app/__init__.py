"""
RCM SaaS Application
A scalable Revenue Cycle Management SaaS platform for Indian hospitals
"""

__version__ = "1.0.0"
__author__ = "RCM SaaS Team"

# Expose a top-level Flask app for WSGI servers expecting `app:app`
try:
    from .main import create_app  # type: ignore
    app = create_app()  # noqa: F401
except Exception as e:  # pragma: no cover
    # Avoid import-time crashes in environments where config isn't ready yet
    import logging
    logging.error(f"Failed to create app in __init__.py: {e}")
    app = None  # type: ignore