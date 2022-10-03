from flask import Flask,redirect,url_for,render_template,request, session, flash
from models import Question, Assessment, History, User
from utils import require_login, db
import config
import os
from flask_migrate import Migrate
import random

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db) 

ANSWER_MAP = {
    'A':'Option1',
    'B':'Option2',
    'C':'Option3',
    'D':'Option4'
}

# index page
@app.route('/')
@require_login
def home():
    if session.get('role') == 'teacher':
        return redirect(url_for('teacherindex'))
    else:
        return redirect(url_for('studentindex'))

#Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role')
        try:
            user = User.query.filter_by(username = username).filter_by(role = role).first()
            if user:
                if user.password == password:

                    session['id'] = user.id
                    session['username'] = user.username
                    session['role'] = user.role
                    flash('Hello {} !'.format(user.username),'success')
                    if user.role == 'teacher':
                        return redirect(url_for('teacherindex'))
                    else:
                        return redirect(url_for('studentindex'))
                else:
                    flash('Username and password not matched!', 'danger')
                    return redirect(url_for('login'))
            else:
                flash('Username not exists!', 'danger')
                return redirect(url_for('login'))
        except Exception as e:
            flash('Exception, please try it later!','danger')
            return redirect(url_for('login'))
    else:
        return render_template("login.html")

#Logout
@app.route('/logout')
@require_login
def logout():
    session.clear()
    flash('Logout!','success')
    return redirect(url_for('login'))


@app.route('/addquestion', methods=['GET', 'POST'])
@require_login
def addquestion():
    if request.method == 'POST':
        try: 
            question = request.form.get('question')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            answer = request.form.get('answer')
            explain = request.form.get('explain')

            record = Question.query.filter_by(question=question).first()
            if record:
                flash('The question exists, please input another one!','danger')
                return redirect(url_for('questions'))
            else:
                record = Question(
                            question = question,
                            option1 = option1,
                            option2 = option2,
                            option3 = option3,
                            option4 = option4,
                            answer = answer,
                            explain = explain
                            )
                db.session.add(record)
                db.session.commit()
                flash('Question is added!','success')
                return redirect(url_for('questions'))
        except Exception as e:
            print('exception - {}'.format(str(e)))
            flash('Exception, please try it later!','danger')
            return redirect(url_for('questions'))
    else:
        return render_template("add_question.html")

#delete question
@app.route('/delquestion/<id>', methods=['GET','POST'])
@require_login
def delquestion(id):
    try:
        record = Question.query.get_or_404(id)
        # db.session.delete(record)
        record.status = False
        db.session.commit()
        flash('The question is deleted!','success')
        return redirect(url_for('questions'))
    except Exception as e:
        print('exception - {}'.format(str(e)))
        flash('Exception, please try it later!','danger')
        return redirect(url_for('questions'))

#edit question
@app.route('/editquestion/<id>', methods=['GET','POST'])
@require_login
def editquestion(id):
    record = Question.query.get_or_404(id)
    if request.method == 'POST':
        try: 
            question = request.form.get('question')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            answer = request.form.get('answer')
            explain = request.form.get('explain')
            
            record.question = question
            record.option1 = option1
            record.option2 = option2
            record.option3 = option3
            record.option4 = option4
            record.answer = answer
            record.explain = explain
            db.session.commit()
            flash('The question is updated!','success')
            return redirect(url_for('questions'))
        except Exception as e:
            print('exception - {}'.format(str(e)))
            flash('Exception, please try it later!','danger')
            return redirect(url_for('questions'))
    else:
        return render_template('edit_question.html', question=record, ANSWER_MAP=ANSWER_MAP)


#questions
@app.route('/questions', defaults={'page':1})
@app.route('/questions/page/<int:page>')
@require_login
def questions(page):
    questions_query = Question.query.filter_by(status = True)
    paginate = questions_query.order_by(Question.id).paginate(page, 10)
    return render_template('questions.html', questions = paginate.items, paginate=paginate)

# generate assessment
@app.route('/generate', methods=['GET', 'POST'])
@require_login
def generate():
    if request.method == 'POST':
        try: 
            title = request.form.get('title')
            question_ids = request.form.get('question_ids')
            category = request.form.get('category')
            duration_time  = request.form.get('duration_time')
            due_time = request.form.get('due_time')

            record = Assessment(
                        title = title,
                        question_ids = question_ids,
                        category = category,
                        duration_time = duration_time,
                        due_time = due_time
                        )
            db.session.add(record)
            db.session.commit()
            flash('Assessment is added!','success')
            return redirect(url_for('assessments'))
        except Exception as e:
            print('exception - {}'.format(str(e)))
            flash('Exception, please try it later!','danger')
            return redirect(url_for('generate'))
    else:
        all_questions = Question.query.filter_by(status=True).all()
        questions = random.sample(all_questions, 10)
        print(questions)
        question_ids = [question.id for question in questions]
        str_question_ids = ",".join([str(id) for id in sorted(question_ids)])
        # question_ids = ",".join([question.id for question in questions])
        return render_template('generate_assessment.html', questions=questions, question_ids=question_ids, str_question_ids=str_question_ids)

#assessments
@app.route('/assessments')
@require_login
def assessments():
    assessments_query = Assessment.query
    category = request.args.get('category')
    if category in ['formative', 'summative']:
        assessments = assessments_query.filter_by(category = category).all()
    else:
        assessments = assessments_query.all()
    return render_template('assessments.html', assessments=assessments)

# # show all accessments
# @app.route('/assessments')
# @require_login
# def assessments(page):
#     records_query = Assessment.query
#     category = request.args.get('category')
#     if category:
#         records = records_query.filter_by(category = category).all()
#     else:
#         records = records_query.all()
#     return render_template('assessments.html', records=records)

# take examination
@app.route('/examine/<id>', methods=['GET', 'POST'])
@require_login
def examine(id):
    assessment = Assessment.query.filter_by(id = id).first()
    if assessment.category == 'summative':
        record = History.query.filter_by(assessment_id = assessment.id, student_name = session.get('username')).first()
        if record:
            flash('This assessment only for one time, time, you have examine it already!', 'danger')
            return redirect(url_for("assessments"))
    question_ids = [int(qid) for qid in assessment.question_ids.split(",")]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()
    answers = [quesiton.answer for quesiton in questions]

    if request.method == 'POST':
        try:
            reply_1 = request.form.get('reply_1')
            reply_2 = request.form.get('reply_2')
            reply_3 = request.form.get('reply_3')
            reply_4 = request.form.get('reply_4')
            reply_5 = request.form.get('reply_5')
            reply_6 = request.form.get('reply_6')
            reply_7 = request.form.get('reply_7')
            reply_8 = request.form.get('reply_8')
            reply_9 = request.form.get('reply_9')
            reply_10 = request.form.get('reply_10')

            replys = [reply_1, reply_2, reply_3, reply_4, reply_5, reply_6, reply_7, reply_8, reply_9, reply_10]
            records = History.query.filter_by(assessment_id = assessment.id, student_name = session['username']).all()

            score = 0
            times = 1
            if len(records) > 0:
                times = len(records) + 1

            for i in range(10):
                if replys[i] == answers[i]:
                    score += 10

            record = History(
                assessment_id = assessment.id,
                title = assessment.title,
                question_ids = assessment.question_ids,
                student_name = session['username'],
                replys = ",".join(replys),
                times = times,
                score = score, 
                category = assessment.category
                )
            db.session.add(record)
            db.session.commit()
            flash('Examination is completed！', 'success')
        except Exception as e:
            print(e)
            flash('Exception, please try it later!','danger')
            return redirect(url_for("examine", id=id))
        return redirect(url_for("examine", id=id))
    else:
        return render_template('examine.html', assessment=assessment, questions=questions, question_ids=question_ids)

#show history
@app.route('/historys')
@require_login
def historys():
    records_query = History.query
    if session.get('role') == 'student':
        records = records_query.filter_by(student_name = session.get('username')).all()
    else:
        records = records_query.all()
    return render_template('historys.html', historys=records)

# @app.route('/history/<id>')
# @require_login
# def history(id):
#     history = History.query.filter_by(id=id, student_name = session.get('username')).first()
#     questions = Question.query.filter_by(id_in=history.quesiton_ids).all()
#     return render_template('history.html', questions=questions, history=history)

@app.route('/showdetail/<id>')
@require_login
def showdetail(id):
    if session.get('role') == 'teacher':
        history = History.query.filter_by(id=id).first()
    else:
        history = History.query.filter_by(id=id, student_name = session.get('username')).first()

    question_ids = [int(qid) for qid in history.question_ids.split(",")]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()

    replys = history.replys.split(',')
    return render_template('exam_detail.html', questions=questions, history=history, replys = replys)

@app.route('/studentindex')
@require_login
def studentindex():
    return render_template('studentindex.html')


@app.route('/teacherindex')
@require_login
def teacherindex():
    return render_template('teacherindex.html')


if __name__ == '__main__':
    app.run(port=8080,debug=True)