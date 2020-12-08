import ntpath
import os
import sys
from collections import OrderedDict
from datetime import datetime


import app.helpers as helpers
from flask import render_template, url_for


def prepare(checksum=1):
    categories = helpers.read_yaml_file(helpers.abs_path('settings', 'categories.yaml'))
    site = helpers.read_yaml_file(helpers.abs_path('settings', 'site.yaml'))
    styles = helpers.get_styles(site)

    render_home_page(styles, site, categories)
    render_pages()
    render_posts(checksum, site, categories, styles)


def render_posts(checksum, site, categories, styles):
    markdown_file_paths = list(helpers.get_markdown_posts_list())
    posts = helpers.read_yaml_file(helpers.abs_path('settings', 'posts.yaml'))

    for k, file_path in enumerate(markdown_file_paths):
        abs_post_name = ntpath.basename(file_path)[:-3]
        post_meta = posts[abs_post_name]

        if post_meta.get('draft') is True:
            helpers.stdout(f'Draft      : {abs_post_name}, skipping...', helpers.cli_colors.BLUE)
            continue

        if checksum == 1 and helpers.is_same_checksum(file_path):
            helpers.stdout(f'No changes : {abs_post_name}, skipping...', helpers.cli_colors.WARNING)
            continue
        else:
            helpers.stdout(f'Converting : {abs_post_name}...')

        try:
            html = helpers.convert_markdown_to_html(file_path)
        except Exception as e:
            helpers.stderr(str(e))
            sys.exit(1)

        category = categories[post_meta.get('category')]
        output = render_template('post.html.jinja2',
                                 style=styles,
                                 page_url=url_for('app.view_post', cat=post_meta.get('category'), post=abs_post_name),
                                 page_id=f'{post_meta.get("category")}-{abs_post_name}',
                                 post=html,
                                 meta=post_meta,
                                 slug=abs_post_name,
                                 site=site,
                                 category=category,
                                 title='{category} - {title}'.format(category=category.get('name'),
                                                                     title=post_meta['title']),
                                 )

        os.makedirs(helpers.abs_path('var', 'posts', post_meta.get('category')), exist_ok=True)

        with open(helpers.abs_path('var', 'posts', post_meta.get('category'), abs_post_name + '.html'),
                  'w') as post_file:
            post_file.write(helpers.minify_html(output))

        helpers.add_to_manifest(abs_post_name, helpers.get_file_checksum(file_path))


def get_ordered_posts():
    posts = helpers.read_yaml_file(helpers.abs_path('settings', 'posts.yaml'))
    posts = {key: value for key, value in posts.items() if value.get('draft') is not True}
    return OrderedDict(
        sorted(posts.items(), key=lambda t: datetime.strptime(t[1].get('published_at'), '%d %B, %Y'),
               reverse=True)).items()


def render_home_page(styles, site, categories):
    with open(helpers.abs_path('var', 'pages', 'index.html'), 'w') as file:
        output = render_template('index.html.jinja2',
                                 style=styles,
                                 site=site,
                                 posts=get_ordered_posts(),
                                 categories=categories, title=site.get('title'))
        file.write(helpers.minify_html(output))


def render_pages():
    for file in helpers.get_markdown_pages_list():
        helpers.save_html_page_from_mrakdown(file, helpers.abs_path('var', 'pages',
                                                                    ntpath.basename(file).replace('.md', '.html')))