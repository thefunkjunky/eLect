import os

# Change this to DevelopmentConfig when not testing
os.environ["CONFIG_PATH"] = "eLect.config.TestingConfig"

from flask_script import Manager
from eLect.main import app
from eLect.database import Base, engine, session
from tests.api_tests import TestAPI

manager = Manager(app)

@manager.command
def seed_db():
    print("Running seed_db")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    testapi = TestAPI()
    testapi.populate_database()

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    manager.run()

