import psycopg
from flask import Flask
from board import create_app

# Create the Flask application using the factory function defined within __init__.py
app = create_app()

def get_db_connection():
    """A function to connect to the database"""

    connection = psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )

    return connection

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM applicants;')
    applicants = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', applicants=applicants)

if __name__ == "__main__":
    # Start the Flask development server
    app.run(host="0.0.0.0", port=8000, debug=True)