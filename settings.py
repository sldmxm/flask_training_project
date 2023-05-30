import os
import string


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    MIN_URL_LENGTH = 1
    MAX_URL_LENGTH = 256
    SHORT_ID_GENERATE_LENGTH = 6
    SHORT_ID_GENERATE_PATTERN = string.ascii_letters + string.digits
    MIN_CUSTOM_ID_LENGTH = 1
    MAX_CUSTOM_ID_LENGTH = 16
    CUSTOM_ID_PATTERN = r'^[a-zA-Z0-9]+$'
