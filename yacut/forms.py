from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class LinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField('Ваш вариант короткой ссылки')
