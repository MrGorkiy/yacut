from random import choices
# https://docs.python.org/3/library/string.html
from string import ascii_letters, digits

from .models import URLMap


def get_unique_short():
    '''Генерация ссылки.'''
    while True:
        short_id = ''.join(choices(ascii_letters + digits, k=6))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id