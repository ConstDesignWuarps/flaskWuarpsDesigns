from flask import render_template, Blueprint, request, jsonify, url_for, request
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
                         "materials", "renovation", "carpenty", "design",'wood','materials','garden',
                         'framework','woodwork', 'house', 'home', 'carpenter', 'Floor', 'Architect', 
                        'permit']

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


@main.route("/embed/chat", methods=["GET"])
def embed_chat():
    return render_template("main/embed_chat.html")

#--------------------------------------------
Rest
#--------------------------------------------

@main.route("/embed/restaurant", methods=["GET"])
def embed_restaurant_chat():
    return render_template("main/embed_restaurant_chat.html")

@main.route("/restaurant/chat", methods=["POST"])Add commentMore actions
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


#--------------------------------------------
Astrological
#--------------------------------------------

@main.route("/embed/astro", methods=["GET", "POST"])
def embed_astro():
    result = None
    charm_url = None

    if request.method == "POST":
        birthdate_str = request.form.get("birthdate", "").strip()
        try:
            birthdate = datetime.datetime.strptime(birthdate_str, "%d-%m-%Y")
            week_of_year = datetime.datetime.utcnow().isocalendar()[1]

            system_prompt = (
                "Eres un bot astrólogo místico y elegante. Basado en la fecha de nacimiento del usuario "
                "y la semana actual del año, ofrece una explicación cósmica de por qué las cosas pueden no ir bien, "
                "usando un tono poético, espiritual y un poco dramático. Luego, brinda una frase de aliento "
                "llena de esperanza. Finalmente, sugiere un amuleto o tótem de la suerte con un nombre evocador "
                "(por ejemplo, 'gato dorado' o 'pluma de obsidiana'). Responde completamente en español."
            )

            user_prompt = f"Fecha de nacimiento: {birthdate_str}, Semana actual: {week_of_year}"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            message = response.choices[0].message.content.strip()

            # Extract lucky charm
            lucky_charm = None
            for line in message.split('\n'):
                if "amuleto" in line.lower() or "tótem" in line.lower():
                    lucky_charm = line.strip()
                    break

            if lucky_charm:
                charm_url = f"/static/totems/{lucky_charm.lower().replace(' ', '_')}.png"

            result = message

        except Exception as e:
            result = "Hubo un error al consultar los astros."

    return render_template("main/embed_astro_chat.html", result=result, charm_image=charm_url)
