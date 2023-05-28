import re

from flask import jsonify, request

from settings import Config
from . import app
from .exceptions import APIError, NotUniqShortLink
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if url is None:
        raise APIError('Указанный id не найден', 404)
    return jsonify({'url': url.original}), 200


@app.route('/api/id/', methods=['POST'])
def post_new_url():
    data = request.get_json()
    if not data:
        raise APIError('Отсутствует тело запроса')
    if 'url' not in data or not data['url']:
        raise APIError('"url" является обязательным полем!')
    custom_id = data.get('custom_id', '')
    if (
            custom_id and (
            len(custom_id) > Config.MAX_CUSTOM_ID_LENGTH or
            len(custom_id) < Config.MIN_CUSTOM_ID_LENGTH or
            not re.match(Config.CUSTOM_ID_PATTERN, custom_id)
    )):
        raise APIError('Указано недопустимое имя для короткой ссылки')
    try:
        short_url = get_unique_short_id(
            Config.SHORT_URL_LENGTH,
            data['url'],
            data.get('custom_id'),
        )
    except NotUniqShortLink:
        raise APIError(f'Имя "{custom_id}" уже занято.')
    return jsonify({'url': data['url'], 'short_link': short_url}), 201
