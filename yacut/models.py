import re
from datetime import datetime
import random

from flask import url_for

from settings import Config
from . import db
from .exceptions import NotUniqShortLink, APIError


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(Config.MAX_URL_LENGTH),
        nullable=False
    )
    short = db.Column(
        db.String(Config.MAX_CUSTOM_ID_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_by_short_id(short_id):
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def save_to_db(original, short):
        if (
                len(short) > Config.MAX_CUSTOM_ID_LENGTH or
                len(short) < Config.MIN_CUSTOM_ID_LENGTH or
                not re.match(Config.CUSTOM_ID_PATTERN, short)
        ):
            raise APIError('Указано недопустимое имя для короткой ссылки')

        db.session.add(URLMap(
            original=original,
            short=short,
        ))
        db.session.commit()

    @staticmethod
    def get_unique_short_id(original_link, short_id=None):
        """
        В случае наличия проверяет пользовательский короткий ID,
        записывает в БД пользовательский короткий ID,
        при его отсутствии, генерирует и записывает короткий ID
        :param original_link: полная ссылка
        :param short_id: пользовательский короткий ID
        :raise: NotUniqShortLink если пользовательский short_id уже в БД
        :raise: APIError если short_id не прошел валидацию
        :return: абсолютный адрес короткой ссылки
        """
        if original_link.split('://')[0] not in ['http', 'https']:
            original_link = f'https://{original_link}'

        if short_id and URLMap.get_by_short_id(short_id):
            # если короткий id уже есть в БД для того же адреса,
            # было бы логично выдавать его, но нет, тесты против
            # if original_link == get_by_short_id(short_id).original:
            #     return url_for(
            #         "url_redirect",
            #         short_id=short_id,
            #         _external=True
            #     )
            # else:
            raise NotUniqShortLink

        # если уже есть оригинальный урл и нет пожеланий пользователя,
        # выдаем имеющийся в БД id
        elif (
                not short_id and
                URLMap.get_by_short_id(short_id)
        ):
            return url_for(
                "url_redirect",
                short_id=URLMap.query.filter_by(
                    original=original_link).first().short,
                _external=True
            )

        else:
            while not short_id or URLMap.get_by_short_id(short_id):
                short_id = ''.join(
                    random.choices(
                        Config.SHORT_ID_GENERATE_PATTERN,
                        k=Config.SHORT_ID_GENERATE_LENGTH
                    )
                )
            URLMap.save_to_db(
                original_link,
                short_id,
            )
        return url_for("url_redirect", short_id=short_id, _external=True)
