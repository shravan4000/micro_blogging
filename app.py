from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import markdown
import bleach
from markupsafe import Markup
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Secure secret key - use env var in production with fallback for dev
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blogs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Markdown Filter
@app.template_filter('markdown')
def render_markdown(text):
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'b', 'i', 'strong', 'em', 'tt', 'br', 'span',
                    'blockquote', 'code', 'hr', 'ul', 'ol', 'li', 'dd', 'dt', 'img', 'a', 'pre', 'div']
    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title'],
    }
    html = markdown.markdown(text)
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return Markup(clean_html)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(20), nullable=False, default='default_profile.jpg')
    blogs = db.relationship('Blog', backref='author', lazy=True, cascade="all, delete-orphan")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    blogs = db.relationship('Blog', backref='category', lazy=True)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True) # Allowed null for existing blogs
    comments = db.relationship('Comment', backref='blog', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

# Routes
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(Blog.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('index.html', blogs=blogs)

@app.context_processor
def inject_categories():
    return dict(categories=Category.query.all())

@app.route('/blogs')
def blogs():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    query = request.args.get('q')

    sql_query = Blog.query.order_by(Blog.created_at.desc())
    
    if category_id:
        sql_query = sql_query.filter_by(category_id=category_id)
        
    if query:
        search = f"%{query}%"
        sql_query = sql_query.filter(
            (Blog.title.like(search)) | 
            (Blog.description.like(search))
        )
        
    blogs = sql_query.paginate(page=page, per_page=6)
    categories = Category.query.all()
    return render_template('blogs.html', blogs=blogs, query=query, categories=categories)

@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.views += 1
    db.session.commit()
    if request.method == 'POST':
        content = request.form['content']
        
        if contains_offensive_content(content):
            flash('Your comment contains inappropriate content.', 'danger')
            return redirect(url_for('blog', blog_id=blog.id))
            
        new_comment = Comment(content=content, blog_id=blog.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('blog', blog_id=blog.id))
    comments = Comment.query.filter_by(blog_id=blog.id).order_by(Comment.created_at.desc()).all()
    return render_template('blog.html', blog=blog, comments=comments)

@app.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if 'user_id' not in session or blog.user_id != session['user_id']:
        flash('You do not have permission to edit this blog.', 'danger')
        return redirect(url_for('blog', blog_id=blog.id))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form.get('category')
        
        if contains_offensive_content(title) or contains_offensive_content(description):
            flash('Your post contains inappropriate content.', 'danger')
            return redirect(url_for('edit_blog', blog_id=blog.id))
            
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import uuid
            _, ext = os.path.splitext(filename)
            filename = f"{uuid.uuid4().hex}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog.image_file = filename
            
        blog.title = title
        blog.description = description
        blog.category_id = category_id
        db.session.commit()
        flash('Blog updated successfully!', 'success')
        return redirect(url_for('blog', blog_id=blog.id))
    
    return render_template('edit_blog.html', blog=blog)

@app.route('/blog/<int:blog_id>/delete', methods=['POST'])
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if 'user_id' not in session or blog.user_id != session['user_id']:
        flash('You do not have permission to delete this blog.', 'danger')
        return redirect(url_for('blog', blog_id=blog.id))
    
    db.session.delete(blog)
    db.session.commit()
    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Correct hashing method
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists. Please try a different one.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

from profanity_check import predict_prob

def contains_offensive_content(text):
    # predict_prob returns an array of probabilities (0 to 1)
    # We check if the probability of being offensive is > 80%
    if not text or not text.strip():
        return False
    prob = predict_prob([text])
    return prob[0] > 0.8

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        flash('You need to log in to create a blog post.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form.get('category')
        
        if contains_offensive_content(title) or contains_offensive_content(description):
            flash('Your post contains inappropriate content.', 'danger')
            return render_template('create.html')
            
        file = request.files.get('image')
        image_file = 'default.jpg'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Prevent overwrite or collision - simple uuid
            import uuid
            _, ext = os.path.splitext(filename)
            filename = f"{uuid.uuid4().hex}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_file = filename
            
        new_blog = Blog(title=title, description=description, user_id=session['user_id'], category_id=category_id, image_file=image_file)
        db.session.add(new_blog)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create.html')

@app.route('/my_blogs')
def my_blogs():
    if 'user_id' not in session:
        flash('You need to log in to view your blogs.', 'danger')
        return redirect(url_for('login'))
    blogs = Blog.query.filter_by(user_id=session['user_id']).order_by(Blog.created_at.desc()).all()
    return render_template('my_blogs.html', blogs=blogs)

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    blogs = Blog.query.filter_by(author=user).order_by(Blog.created_at.desc()).all()
    return render_template('user_profile.html', user=user, blogs=blogs)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Please log in to edit your profile.', 'danger')
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        bio = request.form['bio']
        
        if contains_offensive_content(bio):
            flash('Your bio contains inappropriate content.', 'danger')
            return redirect(url_for('edit_profile'))
            
        file = request.files.get('profile_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import uuid
            _, ext = os.path.splitext(filename)
            filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_image = filename
            
        user.bio = bio
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile', username=user.username))
        
    return render_template('edit_profile.html', user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Seed categories if not exist
        if not Category.query.first():
            db.session.add(Category(name='Tech'))
            db.session.add(Category(name='Lifestyle'))
            db.session.add(Category(name='Personal'))
            db.session.commit()
    app.run(debug=True)