from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FloatField, BooleanField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class PostRateForm(FlaskForm):
    origin = StringField(_l('Origin City'), validators=[DataRequired()], id='locationTextField1')
    destination = StringField(_l('Destination City'), validators=[DataRequired()], id='locationTextField2')
    equipment_type = SelectField(
        'Equipment Type',
        choices=[('dryvan', 'Dry Van'), ('reefer', 'Reefer'), ('flatbed', 'Flatbed')]
    )
    hazardous_freight = SelectField('Hazardous?', choices=[('Yes',True), ('No', False)])
    brokered_load = SelectField('Was this load through a 3PL or broker?', choices=[('Yes',True), ('No', False)])
    hazardous_freight = BooleanField(_l('Did this load contain hazardous materials?'))
    brokered_load = BooleanField(_l('Was this load through a broker?'))

    weather = SelectField('Weather from 1-5: 5 being the worst weather', choices=[('1',1),
                                                                  ('2', 2),
                                                                  ('3', 3),
                                                                  ('4', 4),
                                                                  ('5', 5)])

    rate_per_mile = FloatField(_l('Rate Per Mile'), validators=[DataRequired()])
    dead_head = IntegerField(_l('How far did you have to deadhead?'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


    def __init__(self, *args, **kwargs):
        super(PostRateForm, self).__init__(*args, **kwargs)


class SearchRatesForm(FlaskForm):
    origin = StringField(_l('Origin City'), validators=[DataRequired(), Length(min=0, max=30)], id='locationTextField1')
    destination = StringField(_l('Destination City'), validators=[DataRequired(), Length(min=0, max=30)], id='locationTextField2')
    equipment_type = SelectField(
        'Equipment Type',
        choices=[('dryvan', 'Dry Van'), ('reefer', 'Reefer'), ('flatbed', 'Flatbed')]
    )
    hazardous_freight = SelectField('Hazardous?', choices=[('Yes',True), ('No', False)])
    submit = SubmitField(_l('Submit'))


    def __init__(self, *args, **kwargs):
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchRatesForm, self).__init__(*args, **kwargs)



class LocationReviewForm(FlaskForm):
    shipper = StringField('Shipper', validators=[DataRequired()])
    consignee = StringField('Consignee', validators=[DataRequired()])
    unloading_score = SelectField('Unloading score 1-5: 5 being the worst', choices=[('1',1),('2', 2), ('3', 3), ('4', 4), ('5', 5)])
    lateness_score = SelectField('Lateness score 1-5: 5 being the worst (Run late all the time)', choices=[('1',1),('2', 2), ('3', 3), ('4', 4), ('5', 5)])
    comments = TextAreaField(_l('Add a comment about unloading'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))
