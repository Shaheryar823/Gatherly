from flask import Flask
from app.utils.db import get_db_connection

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize DB
    get_db_connection(app)

    # Import routes
    from app.routes.auth_routes import auth_bp
    from app.routes.event_routes import event_bp
    from app.routes.social_routes import social_bp
    from app.routes.main_routes import main_bp

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(main_bp)

    return app
