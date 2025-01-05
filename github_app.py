from flask import Flask, redirect, url_for, session
from flask_dance.contrib.github import make_github_blueprint, github
import os,logging
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "my_secret_key"  # Replace with a secure random key

# Create GitHub OAuth Blueprint
github_bp = make_github_blueprint(
    client_id="7417cdeb21b268311a65",  # Replace with your Client ID
    client_secret="23dce2da218b9fcff5d07d428368cc4132d71a9c",  # Replace with your Client Secret
    redirect_to="custom_callback",
)
app.register_blueprint(github_bp, url_prefix="/login")

@app.route("/")
def root():
    return "<a href=\"/github_login\">Login with GitHub</a>"

@app.route("/github_login")
def index():
    if not github.authorized:
        logging.info(f"redirect: {url_for("github.login")}")
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    logging.info(f"github_login resp: {resp}")
    assert resp.ok, resp.text
    user_info = resp.json()
    return f"Hello, {user_info['login']}!"

@app.route("/custom_callback")
def custom_callback():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok, resp.text
    user_info = resp.json()
    return f"Hello, {user_info['login']}!"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)