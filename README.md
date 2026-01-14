![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Flask](https://img.shields.io/badge/flask-web%20framework-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
# Flask-LearnPython

Flask-LearnPython is an interactive learning platform designed to help users learn Python through structured lessons, examples, and AI assistance.
The application focuses on:
- clean backend architecture
- secure user authentication
- controlled execution of user-submitted Python code
- real integrations (AI, payments, database)


## Features
### User Authentication
- Login / logout
- Session-based authentication
- Tier-based access control (free vs premium)

### AI Learning Assistant
- AI-powered explanations and help
- Integrated via OpenAI API
  
### Secure Python Sandbox
- Executes user Python code in a restricted environment
- Prevents unsafe operations
- Designed with security in mind
  
### Payment Integration
- PayPal integration for premium access
- Tier upgrade logic
  
### Security
- CSRF protection
- Input validation
- Secure session handling
  
### Web Application
- Flask backend
- HTML templates + static assets
- SEO support (robots.txt, sitemap)


## Tech Stack
**Backend**
- Python
- Flask
- Flask-CORS
- Flask-WTF (CSRF)
- Flask-Mail

**Database**
- Supabase (PostgreSQL)

**Authentication & Security**
- Flask sessions
- Werkzeug password hashing
- CSRF protection
- Decorator-based access control
- Rate limiting & daily usage limits

**AI**
- OpenAI API (ChatGPT)

**Payments**
- PayPal IPN (Instant Payment Notification)


## Requirements
- Python 3.9+
- pip
- Virtual environment recommended


## Installation
```bash
git clone https://github.com/minkong05/Flask-Learnpython.git
cd Flask-Learnpython
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```


## Environment Variables
Create a .env file in the project root.

### Example (.env.example):
- `SECRET_KEY=your_flask_secret_key`
- `OPENAI_API_KEY=your_openai_api_key`
- `SUPABASE_URL=your_supabase_project_url`
- `SUPABASE_API_KEY=your_supabase_service_key`
- `MAIL_PASSWORD=your_gmail_app_password`
- `WEBHOOK_ID=your_webhook_id`


## Running the App
`python app.py`
then open
`http://127.0.0.1:5000`

## Secure Python Sandbox (Design Note)
User-submitted Python code is executed in a restricted environment:
- No filesystem access
- No OS-level commands
- Limited built-ins
- Execution time controlled
This prevents malicious code execution while still allowing educational experimentation.


## Project Structure
```bash
Flask-Learnpython/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── python_sandbox/        # Secure code execution logic
├── requirements.txt
├── robots.txt
├── sitemap.xml
├── .gitignore
└── README.md
```

## Author

Built by **Kong Yu Min**  
University of Glasgow  
Python / Backend / Security-focused Learning Platform
