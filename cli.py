import click
from flask.cli import with_appcontext

def init_cli(app, db):
    """Initialize CLI commands."""
    
    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """Clear existing data and create new tables."""
        db.create_all()
        click.echo('Initialized the database.')
    
    app.cli.add_command(init_db_command) 