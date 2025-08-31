from flask import Flask
from board import create_app

# Create the Flask application using the factory function defined within __init__.py
app = create_app()


if __name__ == "__main__":
    # Start the Flask development server
    app.run(host="0.0.0.0", port=8000, debug=True)