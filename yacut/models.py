import re
from datetime import datetime
import random
from urllib.parse import urlparse

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

    def save_to_db(self):
        if (
                len(self.short) > Config.MAX_CUSTOM_ID_LENGTH or
                len(self.short) < Config.MIN_CUSTOM_ID_LENGTH or
                not re.match(Config.CUSTOM_ID_PATTERN, self.short)
        ):
            raise APIError('Указано недопустимое имя для короткой ссылки')

        db.session.add(self)
        db.session.commit()
        return self

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
        if not urlparse(original_link).scheme:
            original_link = (
                urlparse(original_link)._replace(scheme='https').geturl()
            )

        if short_id and URLMap.get_by_short_id(short_id):
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
            # Справедливости ради, вероятность генерации занятого адреса
            # равна количеству занятых (а не 1) / количество возможных перестановок,
            # то есть, растет вместе с БД.
            short_id = (
                    short_id or
                    ''.join(random.choices(
                        Config.SHORT_ID_GENERATE_PATTERN,
                        k=Config.SHORT_ID_GENERATE_LENGTH
                    )
                    )
            )
        return url_for(
            "url_redirect",
            short_id=URLMap(
                original=original_link,
                short=short_id,
            ).save_to_db().short,
            _external=True
        )
