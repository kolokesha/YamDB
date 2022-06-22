from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_nums(value):
    """Проверка диапазона оценки от 1 до 10."""

    if not 1 <= value <= 10:
        raise ValidationError(f'оценка {value} должна быть от 1 до 10')


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Год произведения не должен быть больше текущего'
            f' {timezone.now().year}'
        )
    if value <= 0:
        raise ValidationError(
            'Год не может быть нулевым или меньше нуля'
        )


def validate_username(username):
    if username == 'me':
        raise ValidationError('Использовать имя "me" запрещено')
