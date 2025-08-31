from flask import Flask

# Inport the blueprint
from board import pages


def create_app():

    # Create the Flask application instance
    app = Flask(__name__)

    # Register the blueprint defined in pages.py
    app.register_blueprint(pages.bp)
    
    return app


