from __future__ import unicode_literals
from flask import (
    Blueprint, redirect, url_for, render_template, request, flash
)

from fastervibes.db import get_db

bp = Blueprint('index', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        accessCode = request.form['access-code']
        error = None

        if accessCode is None:
            error = 'Access Code Required'
        elif accessCode != '1234':
            error = 'Access Denied'
        else:
            return redirect(url_for("dash.dash"))
        
        flash(error)

    return render_template('index.html.j2')

