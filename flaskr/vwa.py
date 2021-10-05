from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ahardtoguesstext?'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(80))

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(16))
    candidate_descr = db.Column(db.String)
    candidate_photo = db.Column(db.String(50))

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jury_name = db.Column(db.String(16))
    candidate_name = db.Column(db.String(16))
    rating = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=16)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=16)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class AdminForm(FlaskForm):
    candname = StringField('Candidate Name', validators=[InputRequired(), Length(min=2, max=16)])
    candphoto = FileField('Candidate Photo', validators=[InputRequired()])
    canddescr = TextAreaField('Candidate Description', validators=[InputRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if form.username.data == 'admin':
            if check_password_hash('sha256$HI7X6LrbZKZGYM0S$e4f8df0e7d5a95ede1422e1e43bf9e58acbc80202843a20ec309af52aa327090', form.password.data):
                login_user(user)
                return redirect(url_for('adminboard'))
        elif user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            return '<h1>Username is already registered</h1>'
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return '<h1>New user has been created!</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    candidates = Candidate.query.all()
    votes = Votes.query.all()

    if request.method == 'POST':
        if len(votes) != 0: #checking if the jury has already voted
            for i in range(len(votes)):
                if current_user.username == Votes.query.filter_by(jury_name=votes[i].jury_name).first().jury_name:
                    voting_availability = False
                    break
                else:
                    voting_availability = True
        else:
            voting_availability = True

        if voting_availability: #passing votes to the database
            for i in range(len(candidates)):
                prey = Candidate.query.filter_by(candidate_name=candidates[i].candidate_name).first()

                score = request.form.get('score_'+str(i+1))

                new_vote = Votes(jury_name=current_user.username, candidate_name=prey.candidate_name, rating=score)
                db.session.add(new_vote)
                db.session.commit()
        else:
            return 'You have already voted.'

    return render_template('dashboard.html', name=current_user.username, candidates=candidates)

@app.route('/adminboard', methods=['GET', 'POST'])
@login_required
def adminboard():
    if current_user.username == 'admin':
        form = AdminForm()
        candidates = Candidate.query.all()

        if form.validate_on_submit(): #adding to the database
            form.candphoto.data.save(os.path.join('static', form.candphoto.data.filename))
            new_cand = Candidate(candidate_name=form.candname.data, candidate_photo=form.candphoto.data.filename, candidate_descr=form.canddescr.data)
            db.session.add(new_cand)
            db.session.commit()
            return redirect(url_for('adminboard'))
        
        if request.method == 'POST': #deleting from the database
            for i in range(len(candidates)):
                if candidates[i].candidate_name in request.form:
                    prey = Candidate.query.filter_by(candidate_name=candidates[i].candidate_name).first()
                    os.remove(os.path.join('static', prey.candidate_photo))
                    db.session.delete(prey)
                    db.session.commit()
                    break
            return redirect(url_for('adminboard'))

        return render_template('adminboard.html', candidates=candidates, form=form)
    else:
        return redirect(url_for('login'))

@app.route('/results')
@login_required
def results():
    if current_user.username == 'admin':
        votes = Votes.query.all()
        candidates = Candidate.query.all()
        x = {}

        for i in range(len(candidates)):
            x.update({
                candidates[i].candidate_name: {}
                })

        for i in range(len(votes)):
            if votes[i].jury_name in x[votes[i].candidate_name]:
                continue
            else:
                x[votes[i].candidate_name].update({
                    votes[i].jury_name: votes[i].rating
                    })
        
        return jsonify(x)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
