from flask import render_template, Blueprint, request, jsonify, url_for
from mar_tierra import db
from mar_tierra.models import Visit
import openai
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

main = Blueprint('main', __name__)
consent_yes = Blueprint('consent_yes', __name__)

#--------------------------------------------
# Homepage
#--------------------------------------------
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
    db.session.commit()
    return render_template('main/home.html', ip_address=ip_address, consent_given=visit.consent_given)

#--------------------------------------------
# Chatbot routes
#--------------------------------------------
@main.route('/chat/create', methods=['GET'])
def chat_create():
    return jsonify({"link": url_for('homes.new_home')})

@main.route('/chat/build', methods=['GET'])
def chat_build():
    return jsonify({"link": "https://example.com/build"})

CONSTRUCTION_KEYWORDS = [
    "building", "construction", "architecture", "blueprint", "foundation",
    "materials", "renovation", "carpenty", "design", "wood", "garden",
    "framework", "woodwork", "house", "home", "carpenter", "floor", "architect",
    "permit"
]

GREETINGS = ["hi", "hello", "hey", "hola"]

@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()
    predefined_response_flag = not bool(user_message)

    try:
        if predefined_response_flag:
            return jsonify({
                "response": "Please type a message.",
                "show_predefined": True
            })

        if any(greeting in user_message for greeting in GREETINGS):
            return jsonify({
                "response": "Hello! How can I assist you with your construction-related queries?",
                "show_predefined": False
            })

        if any(keyword in user_message for keyword in CONSTRUCTION_KEYWORDS):
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

        return jsonify({
            "response": "Sorry, that's not a construction-related question. Please try ChatGPT for other topics.",
            "show_predefined": False
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            "response": "Sorry, an error occurred. Please try again later.",
            "show_predefined": predefined_response_flag,
            "error": str(e)
        }), 500

#--------------------------------------------
# Embeds
#--------------------------------------------
@main.route("/embed/chat", methods=["GET"])
def embed_chat():
    return render_template("main/embed_chat.html")

@main.route("/embed/restaurant", methods=["GET"])
def embed_restaurant_chat():
    return render_template("main/embed_restaurant_chat.html")

#--------------------------------------------
# Restaurant chatbot
#--------------------------------------------
@main.route("/restaurant/chat", methods=["POST"])
def restaurant_chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    try:
        if not user_message:
            return jsonify({"response": "Please enter a message."})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a restaurant website. Answer questions about menus, hours, and services."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"response": "Sorry, something went wrong.", "error": str(e)}), 500
