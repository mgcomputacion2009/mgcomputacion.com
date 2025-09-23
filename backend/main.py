from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from backend.webhooks.autoresponder_flask import bp_ar


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.register_blueprint(bp_ar)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


