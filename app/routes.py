from flask import Blueprint, render_template, abort, make_response, Response
from app.helpers import read_post, read_html_page, read_yaml_file, abs_path, read_sitemap_page

bp = Blueprint('app', __name__, template_folder='templates', static_folder='static')


@bp.route('/')
def home():
    return read_html_page('index')


@bp.route('/<string:cat>/<string:post>/')
def view_post(cat, post):
    if post := read_post(cat, post):
        return post
    else:
        abort(404)


@bp.route('/about')
def about():
    return read_html_page('about')


@bp.route('/sitemap.xml')
def sitemap():
    return read_sitemap_page()


@bp.errorhandler(404)
def page_not_found(error):
    site = read_yaml_file(abs_path('settings', 'site.yaml'))
    output = render_template('error404.html.jinja2', site=site, title='Page not found')
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': 0
    }
    return make_response(output, 404, headers)
