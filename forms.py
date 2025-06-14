from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, FileField
from wtforms.validators import DataRequired

class LabTestForm(FlaskForm):
    patient_id = SelectField('Patient', validators=[DataRequired()], coerce=int)
    test_name = StringField('Test Name', validators=[DataRequired()])
    notes = TextAreaField('Notes for Lab Technician')

class ProcessLabResultForm(FlaskForm):
    result_value = StringField('Result Value', validators=[DataRequired()])
    reference_range = StringField('Reference Range', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    result_file = FileField('Result File') 