Personal Website

This project is a simple Flask-based personal website with three pages:
* About
* Publications
* Contact

Requirements:
* Python 3.10+
* Flask

You can install Flask with:
python -m pip install Flask

Running the Website
1. Download the module_1 repository to your computer
2. Navigate to the project folder

Create a virtual environment by running the following lines in your terminal:
python -m venv venv
source venv/bin/activate

Run the Flask application in your terminal:
python run.py

Open your Browswer and go to:
http://localhost:8000

File Structure:
* run.py - Entry point to run the Flask app
* board/__init__.py - App factory
* board/pages.py - Routes (About, Publications, Contact)
* templates/ - HTML templates
* static/ - CSS and images
* requirements.txt - Python dependencies
