from .import app
from flask import render_template
import random
import string
from forms import LinkForm
from models import URLMap
from . import app
from flask import redirect, render_template, url_for


LENGTH_OF_LINK = 6


def get_unique_short_id():
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=LENGTH_OF_LINK
        )
    )


@app.route('/')
def index_view():
    form = LinkForm()
    if form.validate_on_submit():
        original_link = form.original_link.data
        new_link = get_unique_short_id()
        while URLMap.query.filter_by(short=new_link).first():
            new_link = get_unique_short_id()
        url_map = URLMap(
            original=original_link,
            short=new_link
        )
        db.session.add(url_map)
        db.session.commit()
        return redirect(url_for('link_view', id=url_map.id))
    return render_template('index.html', form=form)


@app.route('/<int:id>')
def link_view(id):
    link = URLMap.query.get_or_404(id)
    return render_template('index.html', link=link)
