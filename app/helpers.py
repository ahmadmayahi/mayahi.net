import ntpath
import os
import sys
from pathlib import Path

import htmlmin
import urllib3
from flask import render_template

from app.logger import logging
import markdown
import yaml
import json
import hashlib


class cli_colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def abs_path(*paths):
    return os.path.abspath(os.path.join(*list(paths)))


def stdout(msg, color=cli_colors.GREEN):
    sys.stdout.write(color + msg + '\n')


def stderr(msg):
    sys.stderr.write(cli_colors.FAIL + msg + '\n')


def get_markdown_posts_list():
    return Path(abs_path('content', 'posts')).rglob('*.md')


def get_markdown_pages_list():
    return Path(abs_path('content', 'pages')).rglob('*.md')


def convert_markdown_to_html(markdown_file_path):
    try:
        with open(markdown_file_path, "r", encoding="utf-8") as input_file:
            text = input_file.read()
        html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'pymdownx.b64', 'pymdownx.mark',
                                                   'pymdownx.emoji'])
        for el, rep in markdown_bootstrap().items():
            html = html.replace(f'{el}', f'{rep}')

        return html
    except Exception as e:
        logging.exception(e)
        raise e


def save_html_page_from_mrakdown(markdown_file_path, html_file_path):
    html = convert_markdown_to_html(markdown_file_path)
    pages = read_yaml_file(abs_path('settings', 'pages.yaml'))
    name = ntpath.basename(markdown_file_path)[:-3]
    site = read_yaml_file(abs_path('settings', 'site.yaml'))
    styles = get_styles(site)

    with open(html_file_path, 'w', encoding="utf-8") as file:
        html = render_template('page.html.jinja2', title=site.get('title') + ' - ' + pages[name].get('name'), body=html,
                               site=site, style=styles)
        file.write(html)
        file.close()


def markdown_bootstrap():
    return {
        '<h2': '<h2 class="font-bold font-sans break-normal text-gray-900 pt-6 pb-2 text-3xl md:text-2xl"',
        '<h3': '<h3 class="font-bold font-sans break-normal text-gray-900 pt-6 pb-2 text-2xl md:text-xl"',
        '<ul': '<ul class="list-disc list-inside leading-10 pl-8"',
        '<ol>': '<ol class="list-decimal list-inside leading-10 pl-8">',
        '<p>': '<p class="py-2 leading-9">',
        '<pre>': '<pre class="py-3">',
        '<img': '<img class="py-3 md:object-center"',
        '<blockquote>': '<blockquote class="border-l-4 border-teal-500 italic my-8 pl-8 md:pl-12">',
        '<table>': '<div class="table"><table class="table">',
        '</table>': '</table></div>',
    }


def convert_yaml_to_json(yaml_file_path, json_file_path=None):
    yaml_output = read_yaml_file(yaml_file_path)

    if json_file_path is not None:
        with open(json_file_path, "w", encoding="utf-8") as file_write:
            json.dump(yaml_output, file_write)
    else:
        return json.dumps(yaml_output)


def read_json_file(filename):
    with open(filename, "r", encoding="utf-8") as file_json:
        return json.load(file_json)


def read_yaml_file(yaml_file_path):
    return yaml.load(open(yaml_file_path, 'r', encoding="utf-8"), Loader=yaml.FullLoader)


def posts_meta_to_json(posts_yaml_path, save_to):
    yaml_output = read_yaml_file(posts_yaml_path)
    for k, v in yaml_output.items():
        json_path = os.path.join(save_to, k + ".json")
        with open(json_path, "w", encoding="utf-8") as file_write:
            json.dump(v, file_write)


def read_post(category, post):
    try:
        with open(abs_path('var', 'posts', category, post + ".html"), 'r', encoding="utf-8") as html_file:
            return html_file.read()
    except Exception as e:
        return None


def read_html_page(page):
    with open(abs_path('var', 'pages', page + '.html'), 'r', encoding="utf-8") as index:
        return index.read()


def read_sitemap_page():
    with open(abs_path('content', 'sitemap.xml'), 'r', encoding="utf-8") as file:
        return file.read()


def add_to_manifest(key, value):
    manifest_file = abs_path('var', 'manifest.json')
    data = {}

    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding="utf-8") as file:
            data = json.load(file)
            file.close()
    else:
        with open(manifest_file, 'w', encoding="utf-8") as file:
            json.dump({}, file)
            file.close()

    with open(manifest_file, 'w', encoding="utf-8") as file:
        data[key] = value
        json.dump(data, file)
        file.close()


def read_from_manifest(key):
    manifest_file = abs_path('var', 'manifest.json')
    data = {}
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding="utf-8") as file:
            data = json.load(file)
            file.close()

    return data.get(key)


def get_file_checksum(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        content = file.read()
        md5_hash.update(content)
        return md5_hash.hexdigest()


def is_same_checksum(file_path):
    checksum = get_file_checksum(file_path)
    key = read_from_manifest(ntpath.basename(file_path)[:-3])
    return checksum == key


def minify_html(html):
    return htmlmin.minify(html, remove_comments=True, remove_empty_space=True)


def get_styles(site):
    styles = ""

    with open(abs_path('static', 'styles.css'), 'r', encoding="utf-8") as file:
        styles = styles + file.read()

    return htmlmin.minify(styles)
