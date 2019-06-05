from flask_login import logout_user,current_user,login_required,login_user
from estimations import app,db,bcrypt
from estimations.models import Soldier,Team, Question,Questionnaire,Answer

def already_answered(questionnaire_id):
    c_id = current_user.military_id
    answered_questions = Answer.query.filter_by(answerer_military_id = c_id).all()
    for answered_question in answered_questions:
        if answered_question.question.questionnaire_id == questionnaire_id:
            return True
    return False

def register_soldier_to_db(username,military_id,level,team_id):
    soldier = Soldier(username=username, military_id=military_id, level=level)
    soldier.team = Team.query.get(team_id)
    db.session.add(soldier)
    db.session.commit()

def register_team_to_db(teamname):
    team = Team(teamname=teamname)
    db.session.add(team)
    db.session.commit()


def register_question_to_db(question_title,question_min_value,question_max_value,questionnaire_id):
    question = Question(question_title=question_title,
                        question_min_value=question_min_value,
                        question_max_value=question_max_value)
    question.questionnaire = Questionnaire.query.get(questionnaire_id)
    db.session.add(question)
    db.session.commit()


def register_questionnaire_to_db(questionnaire_name):
    questionnaire = Questionnaire(questionnaire_name=questionnaire_name)
    db.session.add(questionnaire)
    db.session.commit()

def validate_admin():
    return current_user.level == 1



def calculate_averages_questionnaire_results_for_team(questionnaire,team,question_title_filter=""):
    sums_for_team = {}
    filled_counter = {}
    for question in questionnaire.questions:
        for answer in question.answers:
            c_id = answer.answerer_military_id
            for soldier in team.users:
                if soldier.military_id == c_id:
                    filled_counter[c_id] = 1
                    if (not (question.question_title in sums_for_team.keys())):
                        sums_for_team[question.question_title] = [1, int(answer.answer_value)]
                    else:
                        sums_for_team[question.question_title][0] += 1
                        sums_for_team[question.question_title][1] += int(answer.answer_value)
                    break
    average_for_teams = {}
    for question_title, stats in sums_for_team.items(): average_for_teams[question_title] = stats[1] / stats[0]


    if len(question_title_filter) > 0:
        filtered_titles = filter(lambda q_title: q_title.__contains__(question_title_filter),average_for_teams.keys())
        n_average_for_teams={}
        for key in filtered_titles: n_average_for_teams[key] = average_for_teams[key]
        average_for_teams = n_average_for_teams

    return average_for_teams,len(filled_counter.keys())

