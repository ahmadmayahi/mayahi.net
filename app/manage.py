from flask import Blueprint
from app.prepare import prepare
import click

bp = Blueprint('manage', __name__, cli_group='manage')


@click.option('--checksum', '-f', default=True, type=bool, required=False, help='Compile markdown files without checksum')
@bp.cli.command("prepare")
def prepare_command(checksum=1):
    prepare(checksum)
