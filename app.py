from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_migrate import Migrate

import os
from dotenv import load_dotenv

import models

from resources.student import blp as StudentBlueprint
from resources.subject import blp as SubjectBlueprint

from flask_cors import CORS
from db import db

# Setup the flask app
app = Flask(__name__)
CORS(app)

load_dotenv()

# Setup the configs
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Student Management System"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.1.0"
app.config["OPENAPI_URL_PREFIX"] = "/"

# Responsible for the documentation website
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Setup what database we are going to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Connect our flask_sqlalchemy to flask
db.init_app(app)
migrate = Migrate(app, db)

# Documentation for API
api = Api(app)
api.register_blueprint(StudentBlueprint)
api.register_blueprint(SubjectBlueprint)

# SETUP A SECRET KEY FOR JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Create a JWT Manager Object
jwt = JWTManager(app)

