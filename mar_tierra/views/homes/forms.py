import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.fields import DateField

from wtforms.validators import DataRequired, ValidationError
from wtforms import SelectField

delta = datetime.timedelta(days=15)


class WeekdayValidator(object):
    def __call__(self, form, field):
        if field.data and field.data.isoweekday() > 5:
            raise ValidationError("Date selected cannot be a weekend.")
        if field.data < datetime.date.today():
            raise ValidationError("The date cannot be in the past!")
        if field.data == datetime.date.today():
            raise ValidationError("The date cannot be today. It needs to be starting tomorrow.")
        if field.data > datetime.date.today() + datetime.timedelta(days=15):
            raise ValidationError("The date cannot be more than 14 days from today, please select a date within "
                                  "the next 14 days.")
        if field.data == datetime.date(2022, 6, 18):
            raise ValidationError("You pick a national holiday, please select another date.")
        if field.data == datetime.date(2022, 12, 30):
            raise ValidationError("Sorry, but we are closed for this day. Please select another date.")
        if field.data == datetime.date(2022, 10, 18):
            raise ValidationError("You pick a national holiday, please select another date.")
            

class NewHomeFom(FlaskForm):
    name = StringField('New Home Project Name', validators=[DataRequired()])
    target_date = DateField('Target Date',  format='%Y-%m-%d', validators=[DataRequired()])

    desired_budget = SelectField('Desired Budget',
                        choices=[('150000', '150000'),('200000', '200000'),
                                 ('225000', '225000'),('250000', '250000'),
                                 ('300000', '300000'),('350000', '350000'),
                                 ('375000', '375000'),('400000', '400000'),
                                 ])

    submit = SubmitField('Submit')
