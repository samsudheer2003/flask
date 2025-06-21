import logging
from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from routes.user_router import user_router
from routes.todo_router import todo_router
from flask_marshmallow import Marshmallow 


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


app.register_blueprint(user_router)
app.register_blueprint(todo_router)

logging.info("Flask App Started")
app_instance = app
if __name__ == '__main__':
    app.run(debug=True)
