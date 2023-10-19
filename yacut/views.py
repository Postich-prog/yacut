import random
import string
from http import HTTPStatus

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import LinkForm
from .models import URLMap

LENGTH_OF_LINK = 6


def get_unique_short_id():
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=LENGTH_OF_LINK)
    )


@app.route("/", methods=["GET", "POST"])
def index_view():
    form = LinkForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form)
    if not form.custom_id.data:
        short_id = get_unique_short_id()
        while URLMap.query.filter_by(short=short_id).first():
            short_id = get_unique_short_id()
    else:
        short_id = form.custom_id.data
        if URLMap.query.filter_by(short=short_id).first():
            flash("Предложенный вариант короткой ссылки уже существует.")
            return render_template("index.html", form=form)
    url_map = URLMap(original=form.original_link.data, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return render_template(
        "index.html",
        form=form,
        url_map=url_for("link_view", short_id=short_id, _external=True),
    )


@app.route("/<string:short_id>", methods=["GET"])
def link_view(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url:
        original = url.original
        return redirect(original)
    abort(HTTPStatus.NOT_FOUND)
