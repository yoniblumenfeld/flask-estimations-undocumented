from flask_wtf import FlaskForm

from wtforms import IntegerField, StringField, SubmitField, BooleanField, TextField, TextAreaField, SelectField,RadioField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange, InputRequired, EqualTo
from estimations.models import Team,Soldier, Questionnaire,Question
from flask_login import current_user

class LoginForm(FlaskForm):
    military_id = IntegerField('Military ID', validators=[DataRequired()])
    submit = SubmitField('Login')


class SoldierRegisterationForm(FlaskForm):
    team = SelectField('Select Team', coerce=int)
    military_id = IntegerField('Military ID', validators=[DataRequired()])
    # Need to create team select field - need to validate that team exists! might need to map team names to team id's
    username = StringField('User Name', validators=[DataRequired()])
    level = SelectField('User Level',coerce=int)
    submit = SubmitField("Register")

    def validate_military_id(self, military_id):
        if len(str(military_id.data)) != 7:
            raise ValidationError('Military ID has to have 7 digits exactly!')
        if Soldier.query.filter_by(military_id=military_id.data).first():
            raise ValidationError("Military ID already exists!")

    def validate_username(self,username):
        if Soldier.query.filter_by(username=username.data).first():
            raise ValidationError('Soldier with such username already exists!')

    def validate_level(self,level):
        if level.data not in range(2):
            raise ValidationError('No such level exists!')

class TeamRegisterationForm(FlaskForm):
    teamname = StringField('Team Name', validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_teamname(self,teamname):
        if Team.query.filter_by(teamname=teamname.data).first():
            raise ValidationError('Team with such teamname already exists!')


class FilterSoldiersForm(FlaskForm):
    team = SelectField('Select Team',coerce=int)
    username = StringField('Username')
    level = SelectField('User Level',coerce=int)
    submit = SubmitField("Filter")

class SoldierUpdateForm(FlaskForm):
    team = SelectField('Select Team', coerce=int)
    military_id = IntegerField('Military ID', validators=[DataRequired()])
    # Need to create team select field - need to validate that team exists! might need to map team names to team id's
    username = StringField('User Name', validators=[DataRequired()])
    level = SelectField('User Level',coerce=int)
    submit = SubmitField("Register")


    def validate_military_id(self, military_id): #still not perfected! need to see what to do when trying to add same military_id
        if len(str(military_id.data)) != 7:
            raise ValidationError('Military ID has to have 7 digits exactly!')
        if Soldier.query.filter_by(military_id=military_id.data).first():
            raise ValidationError("Military ID already exists!")


    def validate_level(self,level):
        if level.data not in range(2):
            raise ValidationError('No such level exists!')

class QuestionnaireRegistrationForm(FlaskForm):
    questionnaire_name = StringField('Questionnaire Name',validators=[DataRequired()])
    submit_questionnaire = SubmitField("Add Questionnaire")

    def validate_questionnaire_name(self,questionnaire_name):
        if Questionnaire.query.filter_by(questionnaire_name=questionnaire_name.data).first():
            raise ValidationError("Questionnaire already exists!")

class QuestionRegistrationForm(FlaskForm):
    question_title = StringField("Question Title",validators=[DataRequired()])
    question_min_value = IntegerField("Min Value",default=1,validators=[DataRequired(),NumberRange(min=1,max=1000)])
    question_max_value = IntegerField("Max Value",default=5 ,validators=[DataRequired(),NumberRange(min=1,max=1000)])
    questionnaire = SelectField('Select Questionnaire', coerce=int)
    submit_question = SubmitField("Add Question")

    def validate_question_title(self,question_title):
        question = Question.query.filter_by(question_title=question_title.data).first()
        if question:
            if question.questionnaire_id == self.questionnaire.data:
                raise ValidationError("Such question title already exists for this questionnaire!")

    def validate_question_min_value(self,question_min_value):
        if question_min_value.data < 0:
            raise ValidationError("Min value lower than 0!")
        if question_min_value.data >= self.question_max_value.data:
            raise ValidationError("Min value has to be lower than max value!")

    def validate_question_max_value(self,question_max_value):
        if question_max_value.data < 0:
            raise ValidationError("Max value lower than 0!")
        if question_max_value.data <= self.question_min_value.data:
            raise ValidationError("Max value has to be greater than min value!")

#class QuestionRegistrationForm(FlaskForm):

class FilterQuestionsForm(FlaskForm):
    question_filter_title = StringField('Question Title')
    questionnaire_filter = SelectField('Questionnaire')
    submit_filter = SubmitField('Filter')

class QuestionUpdateForm(QuestionRegistrationForm):
    submit_question = SubmitField("Update")
    def validate_question_title(self, question_title):
        pass

class QuestionnaireForm(FlaskForm):
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    question_id = IntegerField("Question ID")
    question_title = StringField("Question Title")
    question_value = RadioField("בחר דירוג", coerce=int, validators=[DataRequired()])
    submit_question = SubmitField("Submit")

    def validate_question_value(self,question_value):
        if question_value.data == -1 or not question_value.data:
            raise ValidationError("You must assign a value!")

class FilterStatisticsForm(FlaskForm):
    team_filter = SelectField('Team')
    question_filter_title = StringField('Question Title')
    questionnaire_filter = SelectField('Questionnaire')
    submit_filter = SubmitField('Filter')
