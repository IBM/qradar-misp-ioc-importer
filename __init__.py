import json
import secrets
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from qpylib import qpylib
from qpylib.encdec import Encryption, EncryptionError


# Flask application factory.
def create_app():
    # Create a Flask instance.
    qflask = Flask(__name__)

    # Set up CSRF token protection.
    csrf = CSRFProtect()
    csrf.init_app(qflask)

    # Retrieve QRadar app id.
    qradar_app_id = qpylib.get_app_id()

    # Create unique session cookie name for this app.
    qflask.config['SESSION_COOKIE_NAME'] = 'session_{0}'.format(qradar_app_id)

    # Read in secret key.
    secret_key_store = Encryption({'name': 'secret_key', 'user': 'shared'})
    try:
        secret_key = secret_key_store.decrypt()
    except EncryptionError:
        # If secret key file doesn't exist/fail to decrypt it,
        # generate a new random password for it and encrypt it.
        secret_key = secrets.token_urlsafe(64)
        secret_key_store.encrypt(secret_key)

    qflask.config["SECRET_KEY"] = secret_key

    # Hide server details in endpoint responses.
    @qflask.after_request
    def obscure_server_header(resp):
        resp.headers['Server'] = 'QRadar App {0}'.format(qradar_app_id)
        return resp

    # Register q_url_for function for use with Jinja2 templates.
    qflask.add_template_global(qpylib.q_url_for, 'q_url_for')

    # Initialize logging.
    qpylib.create_log()

    # To enable app health checking, the QRadar App Framework
    # requires every Flask app to define a /debug endpoint.
    # The endpoint function should contain a trivial implementation
    # that returns a simple confirmation response message.
    @qflask.route('/debug')
    def debug():
        return 'Pong!'

    # Import additional endpoints.
    from . import views
    qflask.register_blueprint(views.viewsbp)
    from . import dev
    qflask.register_blueprint(dev.devbp)

    return qflask
