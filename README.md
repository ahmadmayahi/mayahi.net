## mayahi.net

A minimalistic markdown blog written in Python Flask.

This blog is especially created for developers who like to run their markdown blog. 

Features:
* Very lightweight and fast mark.
* YAML based configurations.
* Supports checksum, so, it doesn't convert the posts if no changes were made.
* Supports markdown fenced-code and tables.
* Converts the images into base64.
* Supports categories and pages.
* No external styling.
* Minification.
* Supports highlightjs.
* Support drafts.
 
## Folder structure
* `content/posts`: All the markdown posts has to be placed within this folder (nested folder supported as well).
* `content/pages`: Markdown pages (such as `about`).
* `static/img`: Post images.
* `templates`: Template files.

## How it works
Clone the repository:
```bash
git clone git@github.com:ahmadmayahi/mayahi.net.git
cp .flaskenv.example .flaskenv
```

Create virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate 
```

Install requirements:
```bash
pip3 install -r requirements.txt
```

Compile the markdown files::
```bash
flask manage prepare
```

Run it:
```bash
flask run
```

You should be able to access it via [http://127.0.0.1:500](http://127.0.0.1:500)

## Deploying
I deploy [my blog](https://mayahi.net) using git hooks:
```bash
ssh user@host '
    cd mayahi.net && 
    git pull &&
    source venv/activate &&   
    pip3 install -r requirements.txt && 
    flask manage prepare'
```

Use `flask manage prepare --checksum=0` if you don't want to use the checksum algorithm.