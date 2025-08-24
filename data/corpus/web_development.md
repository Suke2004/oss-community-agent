# Web Development with Python

## Introduction

Python is excellent for web development, offering powerful frameworks and libraries for building web applications, APIs, and dynamic websites.

## Popular Web Frameworks

### Flask

A lightweight, flexible micro-framework perfect for small to medium applications.

#### Basic Flask App

```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/api/users', methods=['GET'])
def get_users():
    users = [
        {'id': 1, 'name': 'John'},
        {'id': 2, 'name': 'Jane'}
    ]
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
```

#### Flask with Templates

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='My App')

@app.route('/user/<username>')
def user_profile(username):
    return render_template('profile.html', username=username)
```

### Django

A full-featured web framework with built-in admin interface, ORM, and security features.

#### Django Project Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── urls.py
    └── templates/
```

#### Django Models

```python
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

#### Django Views

```python
from django.shortcuts import render
from django.http import JsonResponse
from .models import User

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

def user_detail(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return render(request, 'users/detail.html', {'user': user})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
```

## Frontend Integration

### HTML Templates

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ title }}</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='style.css') }}"
    />
  </head>
  <body>
    <h1>{{ title }}</h1>
    <div class="content">{% block content %} {% endblock %}</div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
  </body>
</html>
```

### CSS Styling

```css
/* Basic styling */
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.button:hover {
  background-color: #0056b3;
}
```

### JavaScript Integration

```javascript
// Fetch API for AJAX requests
async function fetchUsers() {
  try {
    const response = await fetch("/api/users");
    const users = await response.json();
    displayUsers(users);
  } catch (error) {
    console.error("Error fetching users:", error);
  }
}

function displayUsers(users) {
  const container = document.getElementById("users-container");
  container.innerHTML = users
    .map(
      (user) =>
        `<div class="user-card">
            <h3>${user.name}</h3>
            <p>ID: ${user.id}</p>
        </div>`
    )
    .join("");
}
```

## Database Integration

### SQLAlchemy (Flask)

```python
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
```

### Django ORM

```python
# Creating objects
user = User.objects.create(name='John', email='john@example.com')

# Querying
users = User.objects.filter(name__icontains='john')
user = User.objects.get(email='john@example.com')

# Updating
user.name = 'John Doe'
user.save()

# Deleting
user.delete()
```

## API Development

### RESTful API with Flask

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'email': user.email
    } for user in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 201
```

### Django REST Framework

```python
from rest_framework import serializers, viewsets

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

## Authentication & Security

### Flask-Login

```python
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    # ... existing fields ...
    password_hash = db.Column(db.String(128))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/protected')
@login_required
def protected():
    return jsonify({'message': 'This is a protected route'})
```

### Django Authentication

```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

@login_required
def profile(request):
    return render(request, 'profile.html')
```

## Deployment

### Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
```

### Production Settings

```python
# settings.py (Django)
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use environment variables for sensitive data
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

### Deployment Platforms

- **Heroku**: Easy deployment for Flask and Django apps
- **AWS**: Scalable cloud infrastructure
- **DigitalOcean**: VPS hosting with app platforms
- **Vercel**: Great for static sites with API routes

## Testing

### Flask Testing

```python
import unittest
from app import app, db

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, World!', response.data)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
```

### Django Testing

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class UserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(name='Test User', email='test@example.com')

    def test_user_list_view(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
```

## Best Practices

1. **Use virtual environments** for project isolation
2. **Follow security best practices** (HTTPS, input validation, etc.)
3. **Write tests** for your code
4. **Use environment variables** for sensitive data
5. **Implement proper error handling**
6. **Use database migrations** for schema changes
7. **Optimize database queries** to avoid N+1 problems
8. **Implement logging** for debugging and monitoring
9. **Use caching** for performance optimization
10. **Follow RESTful conventions** for API design

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Real Python Web Development](https://realpython.com/tutorials/web-dev/)
- [Mozilla Web Development](https://developer.mozilla.org/en-US/docs/Learn)
