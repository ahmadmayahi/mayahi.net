from flask import Blueprint, render_template, abort
from app.helpers import read_post, read_html_page

bp = Blueprint('app', __name__, template_folder='templates', static_folder='static')


@bp.route('/')
def home():
    return read_html_page('index')


@bp.route('/subscribe')
def subscribe():
    return read_html_page('subscribe')


@bp.route('/<string:cat>/<string:post>/')
def view_post(cat, post):
    if post := read_post(cat, post):
        return post
    else:
        abort(404)


@bp.route('/categories')
def categories():
    return 'Categories'


@bp.route('/about')
def about():
    return read_html_page('about')


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html.jinja2'), 404
