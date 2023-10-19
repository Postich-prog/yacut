import re
import string
from http import HTTPStatus
from re import fullmatch

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id

CHARACTERS_SET = string.ascii_letters + string.digits
URL_LOCALHOST = "http://localhost/"


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def get_original_link(short_id):
    original_link = URLMap.query.filter_by(short=short_id).first()
    if not original_link:
        raise InvalidAPIUsage("Указанный id не найден", HTTPStatus.NOT_FOUND)
    return jsonify(url=original_link.original), HTTPStatus.OK


@app.route("/api/id/", methods=["POST"])
def add_id():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage("Отсутствует тело запроса")
    if "url" not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if "custom_id" not in data or not data["custom_id"]:
        custom_id = get_unique_short_id()
        while URLMap.query.filter_by(short=custom_id).first():
            custom_id = get_unique_short_id()
    else:
        if not fullmatch(
            f"[{re.escape(CHARACTERS_SET)}]" + f"{{1,{16}}}", data["custom_id"]
        ):
            raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")
        if URLMap.query.filter_by(short=data["custom_id"]).first() is not None:
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует."
            )
        else:
            custom_id = data["custom_id"]
    url = URLMap()
    data["original"] = data["url"]
    data["short"] = custom_id
    url.from_dict(data)
    db.session.add(url)
    db.session.commit()
    return (
        jsonify(short_link=URL_LOCALHOST + url.short, url=url.original),
        HTTPStatus.CREATED,
    )
