from typing import Callable
from toolz import pipe, curry
from flask import Flask, Blueprint
from flask_cors import CORS
from app.rout.search_routes import create_search_routes

@curry
def apply_cors(app: Flask) -> Flask:
    CORS(app)
    return app

@curry
def register_blueprint(blueprint_factory: Callable[[], Blueprint], app: Flask) -> Flask:
    app.register_blueprint(blueprint_factory())
    return app

@curry
def add_health_check(app: Flask) -> Flask:
    app.add_url_rule(
        '/health',
        'health_check',
        lambda: {"status": "healthy"}
    )
    return app

def create_app() -> Flask:
    return pipe(
        Flask(__name__),
        apply_cors,
        register_blueprint(create_search_routes),
        add_health_check
    )

if __name__ == '__main__':
    print("Starting Elastic server...")
    app = create_app()
    app.run(debug=True, port=5003)