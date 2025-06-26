import logging
from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from routes.user_router import user_router
from routes.todo_router import todo_router
from flask_marshmallow import Marshmallow

bcrypt = Bcrypt()
ma = Marshmallow()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

    
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

   
    app.register_blueprint(user_router, url_prefix='/user')
    app.register_blueprint(todo_router, url_prefix='/todo')

    logging.info("Flask App Created")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
