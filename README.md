# Flask-LearnPython

Flask-LearnPython is a full-stack educational web application designed to help users learn Python through structured learning content, interactive stages, AI-assisted explanations, and secure code execution.  
The platform includes user authentication, subscription-based access control, AI integration, payment handling, and sandboxed code execution.


## Features

- User registration, login, logout (session-based authentication)
- Password reset via email (secure token-based flow)
- Tier-based access control (Free / Standard / Additional / Full Access)
- Structured learning phases, stages, and chapters
- AI-powered Python assistant using OpenAI API
- Daily query limits and rate limiting
- Secure Python code execution via external sandbox service
- PayPal IPN payment handling
- Supabase-backed user and order storage
- CSRF protection and request validation
- SEO support (robots.txt, sitemap.xml)


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


## Project Structure

Flask-LearnPython/

├── app.py  
├── requirements.txt  
├── Procfile  
├── content.json  
├── content2.json  
├── templates/  
├── static/  
├── python-sandbox/  
├── sitemap.xml  
├── robot.txt  
├── README.md  


## Environment Variables

This application uses environment variables loaded via `password.env` or system environment.

### Required Variables
- SECRET_KEY=your_flask_secret_key
- OPENAI_API_KEY=your_openai_api_key

- SUPABASE_URL=your_supabase_project_url
- SUPABASE_API_KEY=your_supabase_service_key

- MAIL_PASSWORD=your_gmail_app_password

- WEBHOOK_ID=your_webhook_id

---

## Authentication & User Management

- Users are stored in Supabase (`users` table)
- Passwords are securely hashed using Werkzeug
- Session-based authentication
- Subscription tiers control access to routes and content
- Daily AI usage is tracked per user


## Learning System

- Content is loaded dynamically from `content.json` and `content2.json`
- Chapters, phases, and stages are rendered using Jinja templates
- Access is restricted based on subscription tier


## AI Assistant

- `/chatgpt` endpoint integrates OpenAI ChatCompletion API
- Python-focused assistant with strict response rules
- Daily query limits enforced per user
- Responses are rendered as HTML using Markdown


## Code Execution Sandbox

- User-submitted Python code is sent to an external sandbox service
- Dangerous keywords are blocked
- Code length is restricted
- Execution timeouts are enforced

Sandbox endpoint:
POST https://learnpython-sandbox.onrender.com/execute


## Payments (PayPal IPN)

- Uses PayPal Instant Payment Notification (IPN)
- Verifies transactions via PayPal servers
- Stores payment records in Supabase (`paypal_orders` table)
- Supports production and sandbox environments


## Security Measures

- CSRF protection enabled
- Password hashing
- Rate limiting
- Daily AI usage limits
- Input validation
- Blacklist-based code execution filtering


## Deployment

- Ready for deployment on platforms like Render or Heroku
- Uses `Procfile` for production startup
- Debug mode disabled in production


## Disclaimer

This project is built for educational and portfolio purposes.
Sensitive keys, credentials, and secrets must be handled securely.


## Author

Built by **Kong Yu Min**  
University of Glasgow  
Python / Backend / Security-focused Learning Platform
