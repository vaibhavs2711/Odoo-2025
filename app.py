from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/rewear'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    points = db.Column(db.Integer, default=0)
    items = db.relationship('Item', backref='uploader', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(100), nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    available = db.Column(db.Boolean, default=True)

class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Men', 'Men'), ('Women', 'Women'), ('Kids', 'Kids'), ('Other', 'Other')], validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    tags = StringField('Tags')
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered')
        else:
            user = User(email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    items = Item.query.filter_by(uploader_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, items=items)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        image_file = request.files.get('image')
        filename = None
        if image_file:
            filename = image_file.filename
            image_path = f'static/uploads/{filename}'
            image_file.save(image_path)
        item = Item(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            type=form.type.data,
            size=form.size.data,
            condition=form.condition.data,
            tags=form.tags.data,
            image_filename=filename,
            uploader_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!')
        return redirect(url_for('dashboard'))
    return render_template('add_item.html', form=form)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)
