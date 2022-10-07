import os, sys

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

import yaml


if os.path.exists("settings.yaml"):
    settings_obj = yaml.safe_load(open("settings.yaml").read().strip())
    APP_DIST = settings_obj["app_dist"]
    CAMP_EXTRA = settings_obj["camp_extra"]
else:
    print("No 'settings.yaml', exiting")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = "SuperStrongAndComplicated"

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://",
)


@app.errorhandler(HTTPException)
def oopsie(e):
    return f"Oops: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def do_stuff():
    if request.method == "GET":
        return render_template(
            "page.html",
            dist=APP_DIST,
            extra=render_template("form.html", dist=APP_DIST, camp_extra=CAMP_EXTRA),
        )
    elif request.method == "POST":
        dtag = request.form["discord-tag"]
        feedback = request.form["feedback"]

        fail = False

        if not "#" in dtag:
            fail = True
        elif len(dtag.split("#")[1]) != 4:
            fail = True

        if not fail:
            if not os.path.exists("data"):
                os.makedirs("data")
            if os.path.exists("data/" + dtag):
                return render_template(
                    "page.html",
                    dist=APP_DIST,
                    extra="<p style='color:red;'>This user has submitted before.</p>",
                )
            else:
                with open("data/" + dtag, "w") as f:
                    f.write(feedback)
                content = f"User: `{dtag}` submitted the following:\n```{feedback}\n```"
                webhook = DiscordWebhook(
                    url=open(".webhook").read().strip(), content=content
                )
                response = webhook.execute()
                return render_template(
                    "page.html", dist=APP_DIST, extra="<p>Thanks for your feedback!</p>"
                )
        else:
            return render_template(
                "page.html",
                dist=APP_DIST,
                extra=f"<p style='color:red;'>Funky discord tag you got there: '{dtag}'</p>",
            )
    else:
        return "How did we get here?"


if __name__ == "__main__":
    app.run(
        host=settings_obj["host"],
        port=settings_obj["port"],
        debug=settings_obj["debug"],
    )
