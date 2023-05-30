from flask import jsonify, request

from . import app
from .exceptions import APIError, NotUniqShortLink
from .models import URLMap


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url = URLMap.get_by_short_id(short_id)
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
    try:
        short_url = URLMap.get_unique_short_id(
            data['url'],
            custom_id,
        )
    except NotUniqShortLink:
        raise APIError(f'Имя "{custom_id}" уже занято.')
    return jsonify({'url': data['url'], 'short_link': short_url}), 201
