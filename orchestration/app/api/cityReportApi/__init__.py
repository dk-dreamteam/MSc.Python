from flask import Blueprint

city_report_bp = Blueprint('city_report', __name__, url_prefix='/api')

from app.api.cityReportApi import routes
