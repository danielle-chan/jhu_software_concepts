from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

# About page
@bp.route("/") # Default page
def about():
    return render_template("pages/about.html")

# Publications page
@bp.route("/publications")
def publications():
    return render_template("pages/publications.html")

# Contact page
@bp.route("/contact")
def contact():
    return render_template("pages/contact.html")