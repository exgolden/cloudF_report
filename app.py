"""
Backend
"""

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route("/")
def homeTEST():
    """
    Home route
    """
    return render_template("base.html")


@app.route("/admin")
def admin():
    """
    Admin route
    """
    return render_template("admin.html")


@app.route("/user")
def user():
    """
    User route
    """
    return render_template("user.html")


@app.route("/download/report")
def download_report():
    return send_from_directory(
        directory="assets", path="report.pdf", as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
