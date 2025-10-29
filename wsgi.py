"""
WSGI entry point for production deployment.

Usage examples:
  gunicorn wsgi:app
  gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
  uwsgi --http :8000 --wsgi-file wsgi.py --callable app
  
For development with debug mode:
  python wsgi.py
  or set FLASK_DEBUG=true python wsgi.py
"""

from app import create_app

app = create_app()
application = app

if __name__ == "__main__":
    # Enable debug mode for development
    debug_mode = app.config.get('DEBUG', True)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

