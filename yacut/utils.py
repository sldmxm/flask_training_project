import string
import random

from flask import url_for

from . import db
from .exceptions import NotUniqShortLink
from .models import URLMap


def get_unique_short_id(length, original_link, short_id=None):
    if original_link.split('://')[0] not in ['http', 'https']:
        original_link = f'https://{original_link}'

    if short_id and URLMap.query.filter_by(short=short_id).first():
        # если короткий id уже есть в БД для того же адреса,
        # было бы логично выдавать его, но нет, тесты против
        # if original_link == URLMap.query.filter_by(
        #         short=short_id).first().original:
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
            URLMap.query.filter_by(original=original_link).first()
    ):
        return url_for(
            "url_redirect",
            short_id=URLMap.query.filter_by(
                original=original_link).first().short,
            _external=True
        )

    else:
        while not short_id or URLMap.query.filter_by(short=short_id).first():
            short_id = ''.join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=length
                )
            )
        db.session.add(URLMap(
            original=original_link,
            short=short_id,
        ))
        db.session.commit()
    return url_for("url_redirect", short_id=short_id, _external=True)
