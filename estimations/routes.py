from flask import render_template, url_for, flash, request, redirect, abort
from flask_login import logout_user, current_user, login_required, login_user
from estimations import app, db, bcrypt
from estimations.forms import LoginForm, SoldierRegisterationForm, TeamRegisterationForm, FilterSoldiersForm, \
    SoldierUpdateForm, QuestionnaireRegistrationForm, QuestionRegistrationForm, FilterQuestionsForm, QuestionUpdateForm, QuestionForm, \
    QuestionnaireForm, FilterStatisticsForm
from estimations.models import Soldier, Team, Question, Questionnaire, Answer
from estimations.utils import validate_admin, register_soldier_to_db, register_team_to_db, register_question_to_db,\
    register_questionnaire_to_db, already_answered, calculate_averages_questionnaire_results_for_team


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        soldier = Soldier.query.filter_by(military_id=form.military_id.data).first()
        if soldier:
            login_user(soldier, remember=True)
            flash("login successful")
            return redirect(url_for('home'))
        else:
            flash("Login unsuccesful")
    return render_template('login.html', form=form, questionnaires = Questionnaire.query.all())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register_soldier', methods=['GET', 'POST'])
@login_required
def register_soldier():
    if not validate_admin():
        abort(403)
    form = SoldierRegisterationForm()
    form.team.choices = [(t.id, t.teamname) for t in Team.query.all()]
    form.level.choices = [(level[0], level[1]) for level in enumerate(range(2))]
    if form.validate_on_submit():
        register_soldier_to_db(form.username.data,form.military_id.data,form.level.data,form.team.data)
        flash("Soldier added successfuly!")
    return render_template('register_soldier.html', form=form, questionnaires = Questionnaire.query.all())


@app.route('/home')
@login_required
def home():
    return render_template('home.html',questionnaires = Questionnaire.query.all())


@app.route('/manage_soldiers', methods=['GET', 'POST'])
@login_required
def manage_soldiers():
    if not validate_admin():
        abort(403)
    soldiers = Soldier.query.all()
    form = FilterSoldiersForm()
    form.team.choices = [(t.id, t.teamname) for t in
                         Team.query.all()]  # populate form.team.choices with data from team's db
    form.team.choices.insert(0, (-1, "All"))  # insert choice to display all teams
    form.level.choices = [(level[0], level[1]) for level in
                          enumerate(range(2))]  # create amount of possible chocies as the amount of possible levels
    form.level.choices.insert(0, (-1, "All"))  # insert choice to display all teams
    teamname = "All"
    if form.validate_on_submit():
        if form.team.data != -1:  # case of All teams chose. no such row in db. needs to be handled like this.
            team = Team.query.get(form.team.data)
            soldiers = Soldier.query.filter_by(team=team)
            teamname = team.teamname
        if len(form.username.data) != 0:
            soldiers = filter(lambda soldier: soldier.username.__contains__(form.username.data), soldiers)
        if form.level.data != -1:  # case level filter is used
            soldiers = filter(lambda soldier: soldier.level == form.level.data, soldiers)
    return render_template('manage_soldiers.html', soldiers=soldiers, form=form, teamname=teamname,questionnaires = Questionnaire.query.all())


@app.route('/soldier/<int:soldier_id>/update', methods=['GET', 'POST'])
@login_required
def update_soldier(soldier_id):
    soldier = Soldier.query.get_or_404(soldier_id)
    if not validate_admin():
        abort(403)
    form = SoldierUpdateForm()
    form.team.choices = [(t.id, t.teamname) for t in Team.query.all()]
    form.level.choices = [(level[0], level[1]) for level in enumerate(range(2))]
    if form.validate_on_submit():
        soldier.military_id = form.military_id.data
        soldier.username = form.username.data
        soldier.level = form.level.data
        soldier.team = Team.query.get(form.team.data)
        db.session.commit()
        flash('Soldier has been updated!', 'success')
    elif request.method == "GET":
        form.military_id.data = soldier.military_id
        form.username.data = soldier.username
        form.level.data = soldier.level
        form.team.data = soldier.team.id
    return render_template('update_soldier.html', form=form,questionnaires = Questionnaire.query.all())


@app.route('/soldier/<int:soldier_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_soldier(soldier_id):
    soldier = Soldier.query.get_or_404(soldier_id)
    if not validate_admin():
        abort(403)
    db.session.delete(soldier)
    db.session.commit()
    return redirect(url_for('manage_soldiers'))


@app.route('/manage_teams', methods=['GET', 'POST'])
@login_required
def manage_teams():
    if not validate_admin():
        abort(403)
    teams = Team.query.all()
    return render_template('manage_teams.html', teams=teams,questionnaires = Questionnaire.query.all())


@app.route('/register_team', methods=['GET', 'POST'])
@login_required
def register_team():
    if not validate_admin():
        abort(403)
    form = TeamRegisterationForm()
    if form.validate_on_submit():
        register_team_to_db(form.teamname.data)
        flash("Team added successfuly!")
    return render_template('register_team.html', form=form,questionnaires = Questionnaire.query.all())


@app.route('/manage_questionnaires', methods=['GET', 'POST'])
@login_required
def manage_questionnaires():
    if not validate_admin():
        abort(403)

    questionnaire_form = QuestionnaireRegistrationForm()
    question_form = QuestionRegistrationForm()
    filter_question_form = FilterQuestionsForm()

    question_form.questionnaire.choices = [(q.id, q.questionnaire_name) for q in Questionnaire.query.all()]
    question_form.questionnaire.choices.insert(0,(-1,"All"))

    filter_question_form.questionnaire_filter.choices = [(q.id, q.questionnaire_name) for q in Questionnaire.query.all()]
    filter_question_form.questionnaire_filter.choices.insert(0,(-1,"All"))
    questions = Question.query.all()
    if request.method == "POST":
        if request.values.get("submit_filter"):
            if int(request.values.get("questionnaire_filter")) != -1:
                filtered_questionnaire = Questionnaire.query.get(int(request.values.get("questionnaire_filter")))
                questions = Question.query.filter_by(questionnaire=filtered_questionnaire)

            if len(request.values.get("question_filter_title")) > 0:
                questions = filter(lambda question: question.question_title.__contains__(filter_question_form.question_filter_title.data),questions)
        else:
            if questionnaire_form.validate_on_submit() and questionnaire_form.submit_questionnaire.data:
                register_questionnaire_to_db(questionnaire_form.questionnaire_name.data)
                flash("Questionnaire added successfuly!")
                return redirect(url_for("manage_questionnaires"))

            if question_form.validate_on_submit() and question_form.submit_question.data:
                register_question_to_db(question_form.question_title.data,
                                        question_form.question_min_value.data,
                                        question_form.question_max_value.data,
                                        question_form.questionnaire.data)
                flash("Question added successfuly!")
                return redirect(url_for("manage_questionnaires"))



    return render_template('manage_questionnaires.html', filter_form = filter_question_form, form=questionnaire_form, form2=question_form,questions = questions,questionnaires = Questionnaire.query.all())

@app.route('/question/<int:question_id>/update', methods=['GET', 'POST'])
@login_required
def update_question(question_id):
    if not validate_admin():
        abort(403)
    question = Question.query.get(question_id)
    form = QuestionUpdateForm()
    form.questionnaire.choices = [(q.id, q.questionnaire_name) for q in Questionnaire.query.all()]
    form.questionnaire.choices.insert(0, (-1, "All"))

    if request.method == "GET":
        #fill form automatically
        form.question_title.data = question.question_title
        form.question_max_value.data = question.question_max_value
        form.question_min_value.data = question.question_min_value
        form.questionnaire.data = question.questionnaire_id
    elif request.method == "POST":
        if form.validate_on_submit():
            question.question_title=form.question_title.data
            question.question_max_value=form.question_max_value.data
            question.question_min_value=form.question_min_value.data
            question.questionnaire_id=form.questionnaire.data
            db.session.commit()
            flash("Question updated successfuly!")
            return redirect(url_for("manage_questionnaires"))
        #handle form assignment
        pass
    return render_template('update_question.html',form=form,questionnaires = Questionnaire.query.all())

@app.route('/question/<int:question_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_question(question_id):
    if not validate_admin():
        abort(403)
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("manage_questionnaires"))

@app.route('/questionnaire/<int:questionnaire_id>/',methods=['GET','POST'])
@login_required
def questionnaire(questionnaire_id):
    questionnaire = Questionnaire.query.get(questionnaire_id)
    questions = questionnaire.questions
    forms = []

    if validate_admin():
        #SHOW EDITABLE QUESTIONNAIRE
        return "<h3>Editable Questionnaire</h3>"
    else:
        #show questionnaire for users
        if request.method == "POST":
            if "submit" in request.values.keys():
                for question in questions:
                    if(str(question.id) in request.values.keys()):
                        flash(request.values.get(str(question.id)))
                        answer = Answer(answer_value=request.values.get(str(question.id)),answerer_military_id=current_user.military_id)
                        answer.question = question
                        db.session.add(answer)
                        db.session.commit()
                        flash("{} Answered on question {} the value {}".format(current_user.military_id,question.question_title,request.values.get(str(question.id))))
            return redirect(url_for('home'))
        elif request.method == "GET":
            if(already_answered(questionnaire_id)):
                flash("Already answered this questionnaire!")
                return redirect(url_for('home'))
        return render_template("questionnaire2.html",questions=questions,forms=forms,forms_len=len(forms),title = questionnaire.questionnaire_name, questionnaire_id=questionnaire_id,questionnaires = Questionnaire.query.all())

@app.route('/statistics',methods=['GET','POST'])
@login_required
def statistics():
    form = FilterStatisticsForm()
    form.questionnaire_filter.choices = [(q.id, q.questionnaire_name) for q in
                                                         Questionnaire.query.all()]
    form.team_filter.choices = [(t.id,t.teamname) for t in Team.query.all()]
    questionnaire = Questionnaire.query.get(1)
    team = Team.query.get(1)

    if request.method == "POST":
        questionnaire = Questionnaire.query.get(int(form.questionnaire_filter.data))
        team = Team.query.get(int(form.team_filter.data))
    elif request.method == "GET":
        form.team_filter.data = 1
        form.questionnaire_filter.data = 1


    average_for_teams,filled_counter = calculate_averages_questionnaire_results_for_team(questionnaire,team,form.question_filter_title.data if form.question_filter_title.data else "" )

    return render_template("statistics.html",form = form,filled_counter=filled_counter, team_size = len(team.users), average_for_teams = average_for_teams,questionnaire_name = questionnaire.questionnaire_name, teamname = team.teamname, questionnaires = Questionnaire.query.all())