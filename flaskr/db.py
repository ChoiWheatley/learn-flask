from __future__ import with_statement
import sqlite3
import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """ `close_db`와 `init_db_command`를 사용하기 위해 실행시점에 등록해야만 한다."""
    app.teardown_appcontext(close_db)  # app이 종료될 때 `close_db`이걸 사용하세요!
    app.cli.add_command(init_db_command)  # 플라스크 커맨드에 `init_db_command`를 추가해주세요
