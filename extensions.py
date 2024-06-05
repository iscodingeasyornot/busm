# The reason this file exists is to avoid circular imports in the application.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()