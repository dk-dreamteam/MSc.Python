from flask import Flask
from app.extensions import db, ma
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)

    from app.api.cityReportApi import city_report_bp
    app.register_blueprint(city_report_bp)

    with app.app_context():
        from app.models import category, status, ticket
        db.create_all()

    return app
