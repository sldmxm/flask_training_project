from flask import render_template, jsonify

from . import app, db
from .exceptions import APIError


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(APIError)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code
