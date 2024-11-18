from flask import render_template, Blueprint, request, jsonify
from mar_tierra import db
from mar_tierra.models import Visit
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Initialize OpenAI with your API keyfrom flask import render_template, Blueprint, request, jsonify
from mar_tierra import db
from mar_tierra.models import Visit
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

main = Blueprint('main', __name__)
consent_yes = Blueprint('consent_yes', __name__)

@main.route("/")
@main.route("/home")
def home():
    ip_address = request.remote_addr
    visit = Visit.query.filter_by(ip_address=ip_address).first()
    if visit:
        visit.visit_count += 1
    else:
        visit = Visit(ip_address=ip_address, visit_count=1, consent_given=False)
        db.session.add(visit)
    db.session.commit()  # Ensure the visit count is saved
    return render_template('main/home.html', ip_address=ip_address, consent_given=visit.consent_given)


# Chat route with updated OpenAI API usage
@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400

    try:
        # Updated API call for OpenAI with the latest syntax
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a construction portal."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"response": bot_reply})

    except Exception as e:
        # Log any errors encountered
        print(f"Unexpected error: {e}")
        return jsonify({"response": "Sorry, an error occurred. Please try again later.", "error": str(e)}), 500

openai.api_key = os.getenv("OPENAI_API_KEY")

main = Blueprint('main', __name__)
consent_yes = Blueprint('consent_yes', __name__)


@main.route("/")
@main.route("/home")
def home():
    ip_address = request.remote_addr
    visit = Visit.query.filter_by(ip_address=ip_address).first()
    if visit:
        visit.visit_count += 1
    else:
        visit = Visit(ip_address=ip_address, visit_count=1, consent_given=False)
        db.session.add(visit)
    db.session.commit()  # Ensure the visit count is saved
    return render_template('main/home.html', ip_address=ip_address, consent_given=visit.consent_given)


# Chat route with updated OpenAI API usage
@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400

    try:
        # Updated API call for OpenAI with the latest syntax
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a construction portal."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": bot_reply})

    except Exception as e:
        # Log any errors encountered
        print(f"Unexpected error: {e}")
        return jsonify({"response": "Sorry, an error occurred. Please try again later.", "error": str(e)}), 500
