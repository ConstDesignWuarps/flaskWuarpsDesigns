from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms import SelectField, TextAreaField, IntegerField


class NewProductFom(FlaskForm):
    name = SelectField(u'Product Family',
                        choices=[('Garden', 'Garden'),('Interior', 'Interior'),
                                 ('Color', 'Color'),('Other', 'Other'),])

    description = TextAreaField('Specifications (Wish list)', validators=[DataRequired()])
    target_cost_estimate = IntegerField('Target Estimate')


    submit = SubmitField('Submit')
