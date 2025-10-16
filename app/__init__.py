from flask import Flask
from app.routes.auth_routes import auth_bp
from app.routes.main_routes import main_bp
from app.routes.event_routes import event_bp
from app.routes.social_routes import social_bp
from app.routes.user_routes import user_bp



def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # (Use from .env later)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(user_bp)



    return app
