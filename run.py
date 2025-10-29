from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use DEBUG from config, or default to True for development
    debug_mode = app.config.get('DEBUG', True)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
