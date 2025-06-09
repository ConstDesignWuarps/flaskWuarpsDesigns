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


@main.route("/embed/restaurant", methods=["GET"])
def embed_restaurant_chat():
    return render_template("main/embed_restaurant_chat.html")

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


@main.route("/embed/astro", methods=["GET"])
def embed_astro_chat():
    return render_template("main/embed_astro_chat.html")

@main.route("/astro/fortune", methods=["POST"])
def astro_fortune():
    data = request.get_json()
    birthdate_str = data.get("birthdate", "").strip()

    try:
        birthdate = datetime.datetime.strptime(birthdate_str, "%d-%m-%Y")
        week_of_year = datetime.datetime.utcnow().isocalendar()[1]

        system_prompt = (
            "Eres un místico astrólogo que habla únicamente en español. Según la fecha de nacimiento del usuario "
            "y la semana actual, debes explicar por qué las cosas podrían estar yendo mal para él/ella esta semana. "
            "Después, brinda una frase elegante de aliento, y sugiere un totem de la suerte (como 'águila dorada' o 'pluma de obsidiana'). "
            "La respuesta debe tener tres partes: 1) justificación astral, 2) frase de consuelo, 3) Una Imagen totem sugerido.
            Para el punto 3 la Imagen debe ser super simple en blanco y negro solo un simobolo pagano"
        )

        user_prompt = f"Fecha de nacimiento: {birthdate_str}, semana actual: {week_of_year}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        # Extract the totem suggestion
        lines = content.split("\n")
        totem_line = next((line for line in lines if "totem" in line.lower() or "tótem" in line.lower()), "")
        totem_name = totem_line.split(":")[-1].strip().lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        charm_url = f"/static/totems/{totem_name}.png" if totem_name else None

        return jsonify({
            "fortune": content,
            "charm_image_url": charm_url
        })

    except Exception as e:
        return jsonify({"response": "Ocurrió un error astral.", "error": str(e)}), 500
