from flask import render_template, Blueprint, request, jsonify, url_for
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


@main.route('/chat/create', methods=['GET'])
def chat_create():
    # Return the link for "Create"
    return jsonify({"link": url_for('homes.new_home')})


@main.route('/chat/build', methods=['GET'])
def chat_build():
    # Placeholder for "Build" link
    return jsonify({"link": "https://example.com/build"})


CONSTRUCTION_KEYWORDS = ["building", "construction", "architecture", "blueprint", "foundation",
                         "materials", "renovation", "carpenty", "desing",'wood','materials','garden',
                         'framework','woodwork']

# Predefined keywords and greetings
GREETINGS = ["hi", "hello", "hey", "hola"]

@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    # Check if user message is empty
    predefined_response_flag = not bool(user_message)

    try:
        # If message is empty, return a predefined response
        if predefined_response_flag:
            return jsonify({
                "response": "Please type a message.",
                "show_predefined": predefined_response_flag
            })

        # Check if the message is a greeting
        if any(greeting in user_message for greeting in GREETINGS):
            return jsonify({
                "response": "Hello! How can I assist you with your construction-related queries?",
                "show_predefined": False
            })

        # Check for construction-related keywords
        if any(keyword in user_message for keyword in CONSTRUCTION_KEYWORDS):
            # Call OpenAI API for construction-related queries
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a construction portal."},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_reply = response.choices[0].message.content.strip()
            return jsonify({
                "response": bot_reply,
                "show_predefined": False
            })

        # Fallback for non-construction-related queries
        return jsonify({
            "response": "Sorry, that's not a construction-related question. Please try ChatGPT for other topics.",
            "show_predefined": False
        })

    except Exception as e:
        # Log any errors encountered
        print(f"Unexpected error: {e}")
        return jsonify({
            "response": "Sorry, an error occurred. Please try again later.",
            "show_predefined": predefined_response_flag,
            "error": str(e)
        }), 500
