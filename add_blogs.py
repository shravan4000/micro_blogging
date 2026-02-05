# filepath: /Users/home/vscode_workspace/flask_app/add_blogs.py
from app import app, db, Blog, User

with app.app_context():
    # Create the database tables if they don't exist
    db.create_all()

    # Create a test user
    user = User(username="testuser", password="testpassword")
    db.session.add(user)
    db.session.commit()

    # Add some initial blog entries for the test user
    blog1 = Blog(title="First Blog Post", description="This is the description of the first blog post.", user_id=user.id)
    blog2 = Blog(title="Second Blog Post", description="This is the description of the second blog post.", user_id=user.id)
    blog3 = Blog(title="Third Blog Post", description="This is the description of the third blog post.", user_id=user.id)

    # Add the blog entries to the session
    db.session.add(blog1)
    db.session.add(blog2)
    db.session.add(blog3)

    # Commit the session to the database
    db.session.commit()

    print("Initial blog entries added.")