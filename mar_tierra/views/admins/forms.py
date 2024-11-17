import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, IntegerField
from wtforms.fields import DateField

from wtforms.validators import DataRequired, ValidationError
from wtforms import SelectField


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


class NewHome_Project_Form(FlaskForm):
    category = SelectField('Category',
                        choices=[('Land', 'Land'),('Plans', 'Plans'),
                                 ('Preparation', 'Preparation'),
                                 ('Concrete Footings and Foundation', 'Concrete Footings and Foundation'),
                                 ('Frame, Side, and Roof the House', 'Frame, Side, and Roof the House'),
                                 ('Plumbing and Electrical', 'Plumbing and Electrical'),
                                 ('AC', 'AC'),('Drywall and Trim', 'Drywall and Trim'),
                                 ('Cabinets, Closets', 'Cabinets, Closets'),
                                 ('Flooring', 'Flooring'),('Final Home-Building','Final Home-Building')
                                 ])

    action = StringField('Action', validators=[DataRequired()])
    description = TextAreaField('Description')
    provider = StringField('Provider', validators=[DataRequired()])
    target_date = DateField('Target Date',  format='%Y-%m-%d', validators=[DataRequired()])
    cost_estimate = IntegerField('Cost Estimate')
    actual_cost = StringField('Actual Cost')
    zip_code = StringField('Zip Code')
    submit = SubmitField('Submit')
