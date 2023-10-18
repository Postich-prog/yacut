from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id
import string
import re
from re import fullmatch

CHARACTERS_SET = string.ascii_letters + string.digits


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    original_link = URLMap.query.filter_by(short=short_id).first()
    if not original_link:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify(url=original_link.original), 200


@app.route('/api/id/', methods=['POST'])
def add_id():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if 'custom_id' not in data or data['custom_id'] == '' or data['custom_id'] is None:
        custom_id = get_unique_short_id()
        while URLMap.query.filter_by(short=custom_id).first():
            custom_id = get_unique_short_id()
    else:
        if not fullmatch(f'[{re.escape(CHARACTERS_SET)}]' + f'{{1,{16}}}', data['custom_id']):
            raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
        if URLMap.query.filter_by(short=data['custom_id']).first() is not None:
            raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')
        else:
            custom_id = data['custom_id']
    url = URLMap()
    data['original'] = data['url']
    data['short'] = custom_id
    url.from_dict(data)
    db.session.add(url)
    db.session.commit()
    return jsonify(short_link='http://localhost/' + url.short, url=url.original), 201
