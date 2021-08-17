from flask_script import Manager, Server
from module import app


# set up the app
manager = Manager(app)
# set python manage.py runserver as run server finction
manager.add_command('runserver', Server())

# Set up the manage 
@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__ == '__main__':
    manager.run()