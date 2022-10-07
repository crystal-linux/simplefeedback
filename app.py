import time, os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    make_response,
    redirect,
)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

from discord_webhook import DiscordWebhook

APP_DIST = "Crystal Linux"

app = Flask(__name__)
app.secret_key = "SuperStrongAndComplicated"

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["20 per day", "5 per hour"],
    storage_uri="memory://",
)


@app.errorhandler(HTTPException)
def oopsie(e):
    return f"Oops: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def do_stuff():
    if request.method == "GET":
        return render_template(
            "page.html", dist=APP_DIST, extra=render_template("form.html")
        )
    elif request.method == "POST":
        dtag = request.form["discord-tag"]
        feedback = request.form["feedback"]
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists("data/" + dtag):
            return "Already submitted"
        else:
            with open("data/" + dtag, "w") as f:
                f.write(feedback)
            content = f"User: `{dtag}` submitted the following:\n```{feedback}\n```" 
            webhook = DiscordWebhook(url=open(".webhook").read().strip(), content=content)
            response = webhook.execute()
            return "Thanks!"
    else:
        return "How did we get here?"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
