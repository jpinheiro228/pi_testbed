import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def reg_domain(db, dom_name, owner):
    error = None
    if db.execute(
        'SELECT name FROM vm WHERE name = ?', (dom_name,)
    ).fetchone() is not None:
        error = 'Domain {} already exists.'.format(dom_name)

    if error is None:
        db.execute(
            'INSERT INTO vm (name, owner) VALUES (?, ?)',
            (dom_name, owner)
        )
        db.commit()

    return error


def get_vms_by_user(db, owner):
    vms = db.execute('SELECT name FROM vm WHERE owner = ?', (owner,))
    my_vms = []
    for row in vms.fetchall():
        my_vms.append(row[0])
    return my_vms


def get_free_usrps(db):
    usrps = db.execute('SELECT id FROM usrp WHERE in_use_on = -1')
    free_usrps = []
    for row in usrps.fetchall():
        free_usrps.append(row[0])
    return free_usrps

def remove_vm(db, dom_name):
    db.execute('DELETE FROM vm WHERE name = ?', (dom_name,))
    db.commit()
