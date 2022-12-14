from re import match

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short

NOT_FOUND_ID = 'Указанный id не найден'
MISSING_REQUEST = 'Отсутствует тело запроса'
URL_REQUIRED_FIELD = '"url" является обязательным полем!'
ERROR_URL = 'Указан недопустимый URL'
ERROR_SHORT_URL = 'Указано недопустимое имя для короткой ссылки'
ID_NOT_FREE = 'Имя "{}" уже занято.'


@app.route('/api/id/<string:short>/', methods=['GET'])
def yacat_redirect_api(short):
    redirect = URLMap.query.filter_by(short=short).first()
    if not redirect:
        raise InvalidAPIUsage(NOT_FOUND_ID, 404)
    return jsonify({'url': redirect.original})


@app.route('/api/id/', methods=['POST'])
def create_short_api():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage(MISSING_REQUEST)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_REQUIRED_FIELD)
    if not match(
            r'^[a-z]+://[^\/\?:]+(:[0-9]+)?(\/.*?)?(\?.*)?$', data['url']):
        raise InvalidAPIUsage(ERROR_URL)
    if not data.get('custom_id'):
        data['custom_id'] = get_unique_short()
    elif URLMap.query.filter_by(short=data['custom_id']).first():
        raise InvalidAPIUsage(ID_NOT_FREE.format(data["custom_id"]))
    elif not match(r'^[A-Za-z0-9_]{1,16}$', data['custom_id']):
        raise InvalidAPIUsage(ERROR_SHORT_URL)
    url_map = URLMap()
    url_map.from_dict(data)
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.to_dict()), 201
