from flask import Flask
from os import getenv
from app.routes import bp as routes
from app.manage import bp as manage

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(manage)

app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SERVER_NAME=getenv('SERVER_NAME')
)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
