from flask import (
    Blueprint, redirect, render_template, request
)

bp = Blueprint('info', __name__, url_prefix='/info')

# @bp.route('/', methods=('GET', 'POST'))
# def info():
