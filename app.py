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
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    item = db.relationship('Item', backref='purchases')

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
    items = Item.query.all()  # Show all items, including demo products
    purchases = Purchase.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', user=current_user, items=items, purchases=purchases)

# Search route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if query:
        items = Item.query.filter(
            (Item.title.ilike(f'%{query}%')) |
            (Item.description.ilike(f'%{query}%')) |
            (Item.tags.ilike(f'%{query}%'))
        ).all()
    else:
        items = Item.query.all()
    return render_template('dashboard.html', user=current_user if current_user.is_authenticated else None, items=items, search_query=query)

# Category filter route
@app.route('/category/<category_name>')
def category(category_name):
    items = Item.query.filter_by(category=category_name).all()
    return render_template('dashboard.html', user=current_user if current_user.is_authenticated else None, items=items, category=category_name)

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
        return render_template('item_added.html', item=item)
    return render_template('add_item.html', form=form)


@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

# Purchase route
@app.route('/purchase/<int:item_id>', methods=['POST'])
@login_required
def purchase(item_id):
    item = Item.query.get_or_404(item_id)
    if not item.available:
        flash('Item is not available.')
        return redirect(url_for('dashboard'))
    # Add purchase record
    purchase = Purchase(user_id=current_user.id, item_id=item.id)
    db.session.add(purchase)
    # Update points
    current_user.points += 10
    item.available = False
    db.session.commit()
    flash('Purchase successful! You earned 10 points.')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

with app.app_context():
    db.create_all()
    # Add example products if none exist
    if Item.query.count() == 0:
        demo_items = [
            Item(title='Men T-Shirt', description='Comfortable cotton t-shirt for men.', category='Men', type='T-Shirt', size='L', condition='New', tags='casual,summer', image_filename='sample1.jpg', uploader_id=1),
            Item(title='Women Dress', description='Elegant evening dress for women.', category='Women', type='Dress', size='M', condition='Like New', tags='party,elegant', image_filename='sample2.jpg', uploader_id=1),
            Item(title='Kids Shorts', description='Fun shorts for kids.', category='Kids', type='Shorts', size='S', condition='Good', tags='play,summer', image_filename='sample3.jpg', uploader_id=1),
            Item(title='Unisex Hoodie', description='Warm hoodie for all.', category='Other', type='Hoodie', size='XL', condition='New', tags='winter,unisex', image_filename='sample4.jpg', uploader_id=1)
        ]
        db.session.bulk_save_objects(demo_items)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
