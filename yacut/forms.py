from flask_wtf import FlaskForm
from wtforms import StringField, URLField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from settings import Config


class UrlForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(Config.MIN_URL_LENGTH, Config.MAX_URL_LENGTH),
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(Config.MIN_CUSTOM_ID_LENGTH, Config.MAX_CUSTOM_ID_LENGTH),
            Regexp(
                Config.CUSTOM_ID_PATTERN,
                message="Только буквы и цифры",
            ),
            Optional(),
        ]
    )
    submit = SubmitField('Создать')
