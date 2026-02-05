# Microblog - Flask Application

A modern, feature-rich blogging platform built with Flask. This application supports user authentication, blog creation with rich text and images, categorization, commenting, and user profiles.

## Features

-   **User Authentication**: Secure Login and Registration.
-   **Blog Management**: Create, Read, Update, and Delete (CRUD) blog posts.
-   **Rich Content**: Support for Markdown and Image Uploads.
-   **Categories**: Organize posts by topic (Tech, Life, Coding, etc.).
-   **Interactive**: Comment system with moderation filter.
-   **User Profiles**: customizable profiles with bios and avatars.
-   **Responsive Design**: Modern UI with glassmorphism effects and mobile support.
-   **Search**: Full-text search for blog posts.

## Prerequisites

-   Python 3.8+
-   pip (Python package manager)

## Local Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd flask_app
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

    *Note: The database (`blogs.db`) will be automatically initialized on the first run using the built-in configuration.*

## Production Deployment

### 1. Environment Configuration

In a production environment, you should use environment variables for sensitive configuration.

-   `SECRET_KEY`: A long, random string for session security.
-   `DATABASE_URL`: Your production database URI (default is SQLite).

### 2. Using Gunicorn

This project includes a `wsgi.py` entry point and `gunicorn` in the requirements for production deployment.

To runs with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

-   `-w 4`: Uses 4 worker processes.
-   `-b 0.0.0.0:8000`: Binds to port 8000 on all interfaces.

### 3. Database Initialization

On a production server (where `app.py` main block doesn't run automatically), you can initialize the database tables and categories using the Flask shell:

```bash
flask shell
>>> from app import db, Category
>>> db.create_all()
>>> if not Category.query.first():
...     db.session.add(Category(name='Tech'))
...     db.session.add(Category(name='Life'))
...     db.session.add(Category(name='Coding'))
...     db.session.commit()
>>> exit()
```

### 4. Static Files

For optimal performance in production, serve the `static` folder using a web server like Nginx or a CDN/WhiteNoise immediately in front of Gunicorn.

## Deployment on Platforms (e.g., Render, Heroku)

1.  **Build Command**: `pip install -r requirements.txt`
2.  **Start Command**: `gunicorn wsgi:app`
3.  **Environment Variables**: Set `SECRET_KEY` in the platform's dashboard.

## License

This project is open source and available under the MIT License.
