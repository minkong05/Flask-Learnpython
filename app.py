# ─── Standard Library ──────────────────────────────────────────────────────────
import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from functools import wraps

# ─── Third-Party Libraries ─────────────────────────────────────────────────────
import requests
import markdown
import openai
from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash

from flask import (
    Flask, render_template, redirect, url_for,
    request, session, jsonify, flash,
    send_from_directory, Response, abort
)

from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import subprocess

# ─── Rate-Limit ────────────────────────────────────────────────────────────────
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
#─────────────────────────────────────────────────────────────────────────────────


# ─── Set-up ─────────────────────────────────────────────────────────────────────
load_dotenv("password.env")

logger = logging.getLogger(__name__)        
logger.setLevel(logging.INFO)               

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
with open(CONTENT_DIR / "content.json", "r", encoding="utf-8") as file:
    content = json.load(file)

with open(CONTENT_DIR / "content2.json", "r", encoding="utf-8") as file:
    content2 = json.load(file)

# ─── Flask App Initialization ──────────────────────────────────────────────────
app = Flask(__name__)

app.config["TESTING"] = ("pytest" in sys.modules) or (os.getenv("TESTING") == "true")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
if not app.config['SECRET_KEY']:
    raise RuntimeError("SECRET_KEY not set")
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')
sandbox_secret = os.getenv("SANDBOX_SECRET")

CORS(app)
csrf = CSRFProtect(app)

supabase = None
def init_supabase():
    global supabase

    # if tests, skip supabase completely
    if app.config.get("TESTING"):
        return

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")

    # in production/dev, these MUST exist
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_API_KEY not set")

    supabase = create_client(supabase_url, supabase_key)

def init_limiter(app):
    # In tests/CI: don’t require Redis
    if app.config.get("TESTING"):
        storage_uri = "memory://"
    else:
        storage_uri = os.getenv("REDIS_URL", "redis://localhost:6379")

    limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=("memory://" if app.config["TESTING"] else os.getenv("REDIS_URL", "redis://localhost:6379")),
    default_limits=["200 per day", "50 per hour"],
    )
    limiter.init_app(app)  

    return limiter


def setup_openai():
    if not openai.api_key:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

webhook = os.getenv('WEBHOOK_ID')

# ─── Rate limit rules (central place) ───────────────────────────────────────────
limiter = init_limiter(app)
LIMITS = {
    # Auth endpoints (brute force / enumeration)
    "REGISTER": "5 per minute; 30 per hour",
    "LOGIN": "5 per minute; 30 per hour",
    "RESET_REQUEST": "5 per minute; 30 per hour",
    "RESET_TOKEN": "5 per minute; 30 per hour",

    # Expensive / abusable endpoints
    "CHATGPT": "10 per minute; 100 per day",
    "RUN_CODE": "5 per minute; 60 per hour",

    # Payment webhooks (prevent spam)
    "PAYPAL_IPN": "30 per minute",

    # Paid content / unlock (your existing one)
    "UNLOCK": "5 per minute",
}
#─────────────────────────────────────────────────────────────────────────────────


# ─── Docker logic ───────────────────────────────────────────────────────────────
def run_in_sandbox(code: str):
    result = subprocess.run(
        [
            "docker", "run",
            "--rm",
            "--network=none",
            "--read-only",
            "--pids-limit=32",
            "--memory=128m",
            "--cpus=0.5",
            "python-sandbox-image"
        ],
        input=code,
        text=True,
        capture_output=True,
        timeout=3
    )
    return result.stdout or result.stderr
#─────────────────────────────────────────────────────────────────────────────────

# ─── User Management & SupaBase Helpers ─────────────────────────────────────────
def require_supabase():
    if app.config.get("TESTING"):
        return

    global supabase
    if supabase is None:
        init_supabase()

class User:
    def __init__(self, id, username, email, password_hash, unlocked_phase, tier_name):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.unlocked_phase = unlocked_phase
        self.tier_name = tier_name
  
def get_user_by_email(email):
    require_supabase()
    response = supabase.table('users').select('*').eq('email', email).execute()
    if response.data:
        user_data = response.data[0]
        return User(
            user_data['id'],
            user_data['username'],
            user_data['email'],
            user_data['password_hash'],
            user_data['unlocked_phase'],
            user_data['tier_name'],
        )
    return None

def create_user(email, username, password_hash):
    require_supabase()
    new_user = {
        'email': email,
        'username': username,
        'password_hash': password_hash,
        'unlocked_phase': 1,
        'tier_name': "No Subscription"
    }
    response = supabase.table('users').insert(new_user).execute()
    return response.data[0] if response.data else None

def update_user_phase(email, new_phase):
    require_supabase()
    supabase.table('users').update({'unlocked_phase': new_phase}).eq('email', email).execute()
#─────────────────────────────────────────────────────────────────────────────────  


# ─── Authentication & Authorization Decorators ──────────────────────────────────
@app.before_request
def log_request():
    """Log the data of each incoming request."""
    app.logger.info(f"IP: {request.remote_addr}, Path: {request.path}, Data: {request.form}")

def get_tier_access(user_email):
    require_supabase()
    response = supabase.table('users').select('tier_name').eq('email', user_email).execute()

    if response.data:
        user = response.data[0]
        tier_name = user.get("tier_name", "No Subscription")
        return tier_name

    return "No Subscription"

def login_required(f):
    """
    Decorator that ensures a user is logged in before accessing a route.
    If the user is not authenticated, redirect them to the login page.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def require_tier(*allowed_tiers):
    """
    Decorator that ensures a user has at least ONE of the required subscription tiers.
    Example usage:
        @require_tier("Additional Learning Materials", "Full Access Plan")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            # User must be logged in first
            if not session.get("logged_in"):
                return redirect(url_for("login"))

            # Get tiers from database (your Supabase function)
            user_tiers = get_tier_access(session.get("email"))

            # Allow access if ANY required tier matches the user's tiers
            if any(tier in user_tiers for tier in allowed_tiers):
                return f(*args, **kwargs)

            # Otherwise redirect to pricing section
            return redirect(url_for("home") + "#pricing")

        return wrapper
    return decorator
        
def check_daily_limit(max_queries=20):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if app.config.get("TESTING"):
                return f(*args, **kwargs)
            
            require_supabase()

            user_email = session.get('email')  # Get the currently logged-in user's email
            if not user_email:
                return jsonify({"error": "Unauthorized"}), 401
            
            # Retrieve the current user's information
            response = supabase.table('users').select('query_count', 'last_query_date').eq('email', user_email).execute()
            user = response.data[0] if response.data else None
            
            if not user:
                return jsonify({"error": "User does not exist"}), 404
            
            today = datetime.utcnow().date()
            query_count = user.get('query_count', 0)
            last_query_date = user.get('last_query_date')
            
           # If it's a new day, reset the query count
            if last_query_date != str(today):
                query_count = 0
                supabase.table('users').update({'query_count': 0, 'last_query_date': str(today)}).eq('email', user_email).execute()
            
            # Check whether the number of queries has exceeded the daily limit
            if query_count >= max_queries:
                return jsonify({"error": "You have reached the daily usage limit."}), 429
            
            # Increment the query count
            supabase.table('users').update({'query_count': query_count + 1}).eq('email', user_email).execute()
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Login, Register & Logout Routes ─────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit(LIMITS["REGISTER"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"status": "error", "message": "Email, username or password missing"}), 400

    if get_user_by_email(email):
        return jsonify({"status": "error", "message": "User already registered"}), 400

    password_hash = generate_password_hash(password)
    new_user = create_user(email, username, password_hash)

    if new_user:
        return jsonify({"status": "success", "message": "Registration successful"}), 200
    else:
        return jsonify({"status": "error", "message": "Registration failed"}), 500  

@app.route('/login',methods=['GET', 'POST'])
@limiter.limit(LIMITS["LOGIN"])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email or password missing"}), 400

    if app.config.get("TESTING"):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    user = get_user_by_email(email)
    if user and check_password_hash(user.password_hash, password):
        session['logged_in'] = True
        session['email'] = user.email
        session['username'] = user.username
        session['unlocked_phase'] = user.unlocked_phase
        session['tier_name'] = user.tier_name
        return jsonify({"status": "success", "message": "Login successful"}), 200

    return jsonify({"status": "error", "message": "Invalid email or password"}), 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('home'))
#───────────────────────────────────────────────────────────────────────────────── 


# ─── Main routes ─────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    return render_template('index.html', logged_in=logged_in)

@app.route('/unlock')
@login_required
@require_tier("Additional Learning Materials", "Standard Tier", "Full Access Plan")
@limiter.limit(LIMITS["UNLOCK"])
def unlock():
    return render_template('unlock.html')
    
@app.route('/phase/<int:phase_number>')
@login_required
@require_tier("Standard Tier", "Full Access Plan")
def phase(phase_number):
    return render_template(f'phase/phase{phase_number}.html')
       
@app.route('/stage/<int:stage_number>')
@login_required
@require_tier("Standard Tier", "Full Access Plan")
def stage(stage_number):
    return render_template(f'stage/stage{stage_number}.html')
     
@app.route('/addtional')
@login_required
@require_tier("Additional Learning Materials", "Full Access Plan")
def addtional():
    return render_template('addtional.html')

@app.route('/learn')
@login_required
@require_tier("Standard Tier", "Full Access Plan")
def learn():
    chp = request.args.get('chp', 'default')  # Get the query parameter, with a default value of 'default'
    
    # Retrieve the chapter content; return a default value if no match is found
    chapter_content = content.get(chp, {
        'title': 'Default Chapter', 
        'des': 'No content found.', 
        'keypoint1': 'None', 
        'keypoint2': 'None', 
        'keypoint3': 'None', 
        'example': '', 
        'task1': 'None', 
        'task2': 'None',
        'phases':'None'})
    return render_template('learn.html', content=chapter_content)

@app.route('/learn2')
@login_required
@require_tier("Additional Learning Materials", "Full Access Plan")
def learn2():
    chp = request.args.get('chp', 'default')  # Get the query parameter, with a default value of 'default'
    
    # Retrieve the chapter content; return the default content if no match is found
    chapter_content2 = content2.get(chp, {
        'title': 'Default Chapter', 
        'des': 'No content found.', 
        'keypoint1': 'None', 
        'keypoint2': 'None', 
        'keypoint3': 'None', 
        'keypoint4': 'None', 
        'keypoint5': 'None', 
        'keypoint6': 'None', 
        'example': '', 
        'task1': 'None', 
        'task2': 'None',
        'stages':'None'})
    return render_template('learn2.html', content2=chapter_content2)

@app.route('/term_and_condition', methods=['GET'])
def term_and_condition():
    return render_template('term_and_condition.html')

@app.route('/get_user_profile', methods=['GET'])
@login_required
def get_user_profile():
    user_email = session.get('email')

    # Directly fetch everything from users table, including tier_name
    require_supabase()
    response = supabase.table('users').select('username, email, query_count, tier_name').eq('email', user_email).execute()

    if not response.data:
        return jsonify({"success": False, "message": "User not found"}), 404

    user = response.data[0]

    # If tier_name is missing or empty, set default
    if not user.get('tier_name') or user['tier_name'].strip() == "":
        user['tier_name'] = "No subscription"

    return jsonify({"success": True, "user": user}), 200
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Pricing routes ──────────────────────────────────────────────────────────────
@app.route('/standard')
@login_required
def standard():
    return render_template('standard.html')

@app.route('/learning_materials')
@login_required
def learning_materials():
    return render_template('learning_materials.html')

@app.route('/full_access_plan')
@login_required
def full_access_plan():
    return render_template('full_access_plan.html')
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Reset Password Section ──────────────────────────────────────────────────────
mail_password = os.getenv('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'learnpython1225@gmail.com'
app.config['MAIL_PASSWORD'] = mail_password
mail = Mail(app)

# Used for token encryption and decryption
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/reset', methods=['GET', 'POST'])
@limiter.limit(LIMITS["RESET_REQUEST"])
def reset():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('reset'))

        user = get_user_by_email(email)
        if user:
            # 1) Generate a token
            token = s.dumps(email, salt='email-reset')

            # 2) Generate the reset link
            reset_url = url_for('reset_with_token', token=token, _external=True)

           # 3) Send the email
            msg = Message('Password Reset Request',
                          sender='learnpython1225@gmail.com',
                          recipients=[email])
            msg.body = f'Hello,\n\nYou recently requested to reset your password. Click on the link below to change your password.\n{reset_url}\n\nIf you did not request this, ignore this email.\n\nThanks!\nLearnPython Team'
            mail.send(msg)
            flash('A reset password link has been sent to your email. Please check your inbox.', 'success')
        else:
            flash('This email address does not exist.', 'error')
        return redirect(url_for('reset'))

    # GET request ⇒ render reset.html for the user to enter their email
    return render_template('reset.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
@limiter.limit(LIMITS["RESET_TOKEN"])
def reset_with_token(token):
    try:
       # Parse the token
        email = s.loads(token, salt='email-reset', max_age=900)  # 15 min valid
    except:
        flash('This link is invalid or has expired!', 'error')
        return redirect(url_for('reset'))

    user = get_user_by_email(email)
    if not user:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('reset'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Please enter a new password and confirm it.', 'error')
            return redirect(url_for('reset_with_token', token=token))

        if new_password != confirm_password:
            flash('The passwords entered do not match.', 'error')
            return redirect(url_for('reset_with_token', token=token))

        hashed_password = generate_password_hash(new_password)
        # Update the database
        require_supabase()
        supabase.table('users').update({'password_hash': hashed_password}).eq('email', email).execute()
        flash('Your password has been reset. Please log in using your new password!', 'success')
        return redirect(url_for('login'))

    # GET request ⇒ display a form for the user to enter new_password and confirm_password
    return render_template('reset_with_token.html', token=token)
# ─────────────────────────────────────────────────────────────────────────────────


# ─── ChatGPT Section ─────────────────────────────────────────────────────────────
@app.route('/chatgpt', methods=['POST'])
@csrf.exempt
@login_required
@limiter.limit(LIMITS["CHATGPT"])
@check_daily_limit(max_queries=20)
def chatgpt():
    data = request.get_json(silent=True) or {}
    user_message = (data.get('message') or "").strip()  

    if len(user_message) == 0:
        return jsonify({"status": "error", "message": "Message is required"}), 400
    if len(user_message) > 500:
        return jsonify({"status": "error", "message": "Your question is too long. Please shorten it."}), 400
    if app.config.get("TESTING"):
        return jsonify({"error": "ChatGPT disabled during testing"}), 503
    
    setup_openai()
    messages = [
        {"role": "system","content": \
            "You are a helpful assistant specializing in Python programming. \
            Your role is to assist the user with Python-related questions, including syntax, libraries, debugging, best practices, and more. \
            Always ensure your responses are detailed, accurate, and complete. \
            If the user's question is unrelated to Python, politely remind them to focus on Python topics. \
            If the user's query is too long or complex, divide your response into smaller, logical parts and indicate 'Continued...' when necessary to ensure completeness. \
            If the question is unclear, ask the user for additional context or examples to better assist them. Your goal is to provide professional, clear, and thorough Python assistance in every response. \
            Explain Python decorators in detail. You must complete your reply in 200 tokens or less, but ensure the response is complete and concise." 
        }
    ]

    messages.append({"role":"user","content":user_message})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=250,
            temperature=0.5,
        )

        reply = response['choices'][0]['message']['content'].strip()
        print(f"ChatGPT: {reply}")

        reply_html = markdown.markdown(reply)
        
        return jsonify({"status": "success", "reply": reply_html}), 200

    except openai.error.OpenAIError as e:
        print("OPENAI ERROR:", repr(e))
        return jsonify({"status": "error", "message": str(e)}), 429

    except Exception as e:
        print("CHATGPT ROUTE ERROR:", repr(e))
        return jsonify({"status": "error", "message": str(e)}), 500
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Code Execution Section ──────────────────────────────────────────────────────
# Update the run_code route with security measures
@app.route('/run_code', methods=['POST'])
@login_required
@limiter.limit(LIMITS["RUN_CODE"])
def run_code():
    # Retrieve the code submitted by the user
    data = request.get_json()
    code = data.get('code', '')

   # Limit the length of the submitted code
    if len(code) > 1000:
        return jsonify({"error": "Code too long"}), 413

    try:
        
        # sandbox_service_url = "https://learnpython-sandbox-ncod.onrender.com/execute"
        sandbox_service_url = "http://localhost:5001/execute"

        if not sandbox_secret and not app.config.get("TESTING"):
            return jsonify({"error": "Sandbox secret not configured"}), 500

        response = requests.post(
            sandbox_service_url,
            json={"code": code},
            headers={"X-SANDBOX-SECRET": sandbox_secret},
            timeout=10
        )

      # Check the response from the sandbox service
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Sandbox error", "details": response.json()}), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Execution timeout"}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Pay-pal Section ─────────────────────────────────────────────────────────────
# Configure the PayPal environment
# PAYPAL_VERIFY_URL = "https://ipnpb.paypal.com/cgi-bin/webscr"  # Production environment
PAYPAL_VERIFY_URL = "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"  # Sandbox environment

@app.route('/paypal/ipn', methods=['POST'])
@csrf.exempt
@limiter.limit(LIMITS["PAYPAL_IPN"])
def paypal_ipn():
    """
    Handle PayPal IPN (Instant Payment Notification) requests.
    """
    try:
        ipn_data = request.form.to_dict()

        # Verify the IPN
        if not verify_ipn(ipn_data):
            logger.warning("IPN verification failed")
            return "IPN Verification Failed", 400

        # Check the payment status
        if ipn_data.get('payment_status') != 'Completed':
            logger.info(f"Ignored payment_status: {ipn_data.get('payment_status')}")
            return "Not a completed payment", 200
        

        # Construct the order data
        order_data = {
            "order_id": ipn_data.get('txn_id'),
            "order_status": ipn_data.get('payment_status'),
            "order_intent": "CAPTURE",
            "order_create_time": ipn_data.get('payment_date'),
            "order_update_time": datetime.utcnow().isoformat(),
            "payer_id": ipn_data.get('payer_id'),
            "payer_email": ipn_data.get('payer_email'),
            "payer_name": f"{ipn_data.get('first_name', '')} {ipn_data.get('last_name', '')}".strip(),
            "payer_status": ipn_data.get('payer_status'),
            "currency_code": ipn_data.get('mc_currency'),
            "amount": ipn_data.get('mc_gross'),
            "capture_id": ipn_data.get('txn_id'),
            "capture_status": "COMPLETED",
            "net_amount": float(ipn_data.get('mc_gross', 0)) - float(ipn_data.get('mc_fee', 0)),
            "paypal_fee": ipn_data.get('mc_fee'),
            "shipping_method": ipn_data.get('shipping_method'),
            "shipping_amount": ipn_data.get('mc_shipping'),
            "shipping_discount": ipn_data.get('shipping_discount'),
            "item_name": ipn_data.get('item_name1'),
            "item_number": ipn_data.get('item_number1'),
            "quantity": ipn_data.get('quantity1'),
            "custom_field": ipn_data.get('custom'),
            "transaction_type": ipn_data.get('txn_type'),
            "payment_type": ipn_data.get('payment_type'),
            "discount_amount": ipn_data.get('discount'),
            "insurance_amount": ipn_data.get('insurance_amount'),
            "receipt_id": ipn_data.get('receipt_id'),
            "transaction_subject": ipn_data.get('transaction_subject'),
            "ipn_track_id": ipn_data.get('ipn_track_id'),
            "shipping_address_recipient_name": ipn_data.get('address_name'),
            "shipping_address_line_1": ipn_data.get('address_street'),
            "shipping_address_admin_area_2": ipn_data.get('address_city'),
            "shipping_address_admin_area_1": ipn_data.get('address_state'),
            "shipping_address_postal_code": ipn_data.get('address_zip'),
            "shipping_address_country_code": ipn_data.get('residence_country'),
            "resource": ipn_data,
            "created_at": datetime.utcnow().isoformat(),
            "resource": ipn_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        order_data = clean_order_data(order_data)
        save_to_database(order_data)

        logger.info(f"IPN processed for order_id={order_data['order_id']}")
        return "OK", 200

    except Exception as e:
        logger.error(f"Error processing IPN: {e}", exc_info=True)
        return "Internal Server Error", 500

def verify_ipn(ipn_data):
    """Validate the IPN (Instant Payment Notification) data."""
    params = ipn_data.copy()
    params['cmd'] = '_notify-validate'
    try:
        response = requests.post(PAYPAL_VERIFY_URL, data=params, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }, timeout=10)
        if response.text == 'VERIFIED':
            return True
        else:
            logger.warning(f"IPN Verification failed. Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error verifying IPN: {e}")
        return False

def clean_order_data(order_data):
    """Clean the order data to ensure all fields are in the correct format."""
    for key, value in order_data.items():
        if isinstance(value, str) and value.strip() == '':
            order_data[key] = None  # Replace empty strings with None
        elif isinstance(value, (float, int)) and value is None:
            order_data[key] = 0  # Replace None values with default values
    return order_data

def save_to_database(order_data):
    """Save order data to the database"""
    require_supabase()
    try:
        existing = supabase.table('paypal_orders').select('*').eq('order_id', order_data['order_id']).execute()
        if len(existing.data) == 0:
            # Insert a new record
            result = supabase.table('paypal_orders').insert(order_data).execute()
            if result.data:
                logger.info(f"Inserted new order record: {result.data[0]['id']}")
            else:
                logger.warning("Insert returned empty data")
        else:
            # Update an existing record
            update_fields = order_data.copy()
            update_fields.pop('created_at', None)  # Preserve the original creation timestamp
            result = supabase.table('paypal_orders').update(update_fields).eq('order_id', order_data['order_id']).execute()
            if result.data:
                logger.info(f"Updated existing order record: {result.data[0]['id']}")
            else:
                logger.warning("Update returned empty data")
    except Exception as e:
        logger.error(f"Error saving order to database: {e}", exc_info=True)
        raise
# ─────────────────────────────────────────────────────────────────────────────────


# ─── Other Route ─────────────────────────────────────────────────────────────
@app.route('/<filename>')
def serve_root_files(filename):
    return send_from_directory('.', filename)

# ─────────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=False)