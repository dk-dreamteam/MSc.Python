# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# 1. Database ORM
# We initialize it here without the 'app' object.
db = SQLAlchemy()

# 2. Cross-Origin Resource Sharing
# Allows external clients (like your Streamlit dashboard or a web frontend) to make requests to this API.
cors = CORS()

# 3. Object Serialization / Validation
# Used in the schemas/ folder to easily convert SQLAlchemy models to JSON and validate inputs.
ma = Marshmallow()