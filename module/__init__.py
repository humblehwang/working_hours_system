from datetime import timedelta
from flask_cors import CORS

from flask import Flask, render_template, Blueprint
from flask_bootstrap import Bootstrap
from module.working_hours import working_hours_api



from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
app = Flask(__name__)
CORS(app)
app.register_blueprint(working_hours_api, url_prefix='/')

app.config['TEMPLATES_AUTO_RELOAD'] = True      
app.jinja_env.auto_reload = True



# Here you can globally configure all the ways you want to allow JWTs to
# be sent to your web application. By default, this will be only headers.
#app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]

# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_SECRET_KEY"] = "humblehwang"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=365)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=365)
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)
