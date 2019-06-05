from estimations import db,app,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Soldier.query.get(int(user_id))


class Team(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    teamname = db.Column(db.String(30),nullable=False,unique=True)
    users = db.relationship('Soldier',backref='team',lazy=True)

    def __repr__(self):
        return "Team('{}')".format(self.teamname)

class Soldier(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    military_id = db.Column(db.Integer,nullable=False,unique=True)
    username = db.Column(db.String(30),nullable=False,unique=True)
    level = db.Column(db.Integer,default=0)
    team_id = db.Column(db.Integer,db.ForeignKey('team.id'),nullable=False)

    def __repr__(self):
        return "Soldier('{}','{}','{}')".format(self.username,self.military_id,self.level)

class Questionnaire(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    questionnaire_name = db.Column(db.String(30),nullable=False,unique=True)
    questions = db.relationship('Question',backref='questionnaire',lazy=True)

    def __repr__(self):
        return "Questionnaire('{}')".format(self.questionnaire_name)

class Question(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question_title = db.Column(db.String(30),nullable=False)
    question_min_value = db.Column(db.Integer,nullable=False,default=0)
    question_max_value = db.Column(db.Integer,nullable=False,default=1)
    questionnaire_id = db.Column(db.Integer,db.ForeignKey('questionnaire.id'),nullable=False)
    answers = db.relationship('Answer',backref='question',lazy=True)

    def __repr__(self):
        return "Question('{}','{}','{}')".format(self.question_title,self.question_min_value,self.question_max_value)

class Answer(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    answer_value = db.Column(db.Integer,nullable=False)
    #need to added relationship to answerer
    answerer_military_id = db.Column(db.Integer,nullable=False)
    question_id = db.Column(db.Integer,db.ForeignKey('question.id'),nullable=False)
    def __repr__(self):
        return "Answer('{}')".format(self.answer_value)