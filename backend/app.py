from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from config.settings import get_settings
from routes.query import create_query_blueprint
from services.pipeline_service import PipelineService


def create_app() -> Flask:
    settings = get_settings()
    app = Flask(__name__)
    CORS(app)

    pipeline_service = PipelineService(settings)
    app.register_blueprint(create_query_blueprint(pipeline_service))
    return app


if __name__ == "__main__":
    settings = get_settings()
    app = create_app()
    app.run(host=settings.app_host, port=settings.app_port, debug=settings.debug)
