from flask import render_template, Blueprint, request, jsonify, url_for, session, current_app
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


@main.route("/embed/walter", methods=["GET"])
def embed_walter_chat():
    return render_template("main/embed_walter_chat.html")

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


#--------------------------------------------
# Astro prompt & chatbot
#--------------------------------------------

@main.route("/embed/astro", methods=["GET", "POST"])
def embed_astro():
    result = None
    charm_url = None

    if request.method == "POST":
        birthdate_str = request.form.get("birthdate", "").strip()

        try:
            # HTML5 <input type="date"> returns 'YYYY-MM-DD'
            birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d")

            # Optional: format it to 'DD-MM-YYYY' if you want to show it that way in prompt
            birthdate_display = birthdate.strftime("%d-%m-%Y")

            week_of_year = datetime.datetime.utcnow().isocalendar()[1]

            system_prompt = (
                "Eres un astrólogo místico y dramático. "
                "Escoge aleatoriamente **uno** de estos cuerpos celestes: Saturno, Marte, Venus, Júpiter, Urano, Neptuno, Plutón, el Sol, Andromeda, Mercurio, La Luna. "
                "Usa ese cuerpo como la causa de una dificultad esta semana. "
                "Incluye tres partes:\n\n"
                "Predicción: describe qué problema causa ese cuerpo.\n"
                "Frase: una frase divertida o elegante que la persona pueda decir para culpar a ese cuerpo celeste.\n"
                "Símbolo: un amuleto de la suerte, con un nombre y un símbolo visual (ej. ✦, ✧, ⊛, ‡).\n\n"
                "⚠️ Usa el mismo planeta en la predicción y en la frase.\n"
                "Responde en español. Formato siempre debe tener esas tres líneas exactas."
            )

            user_prompt = f"Fecha de nacimiento: {birthdate_display}, Semana del año: {week_of_year}"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            message = response.choices[0].message.content.strip()

            # Extract lucky charm (totem) line
            lucky_charm = None
            for line in message.split('\n'):
                if "amuleto" in line.lower() or "símbolo" in line.lower():
                    lucky_charm = line.strip()
                    break

            if lucky_charm:
                # Basic image filename based on simplified charm name
                sanitized = lucky_charm.lower().replace(' ', '_').replace(':', '').replace(',', '').replace('.', '')
                charm_url = f"/static/totems/{sanitized}.png"

            result = message

        except Exception as e:
            result = "Hubo un error al consultar los astros."

    return render_template("main/embed_astro_chat.html", result=result, charm_image=charm_url)



@main.route("/walter/chat", methods=["POST"])
def walter_chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    try:
        if not user_message:
            return jsonify({"response": "Por favor, dime algo para poder iluminar tu camino. 🌠"})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Walter Mercado, el legendario astrólogo y vidente. "
                        "Respondes a todo con elegancia, dramatismo, amor incondicional y sabiduría astral. "
                        "Hablas en español con frases cósmicas, referencias al universo y bendiciones. "
                        "Siempre das esperanza y cierras tus mensajes con una frase como: "
                        "'¡Mucho, mucho amor!' o 'Las estrellas te guían, pero el corazón decide.'"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )

        # Add the "Walter Mercado dice..." wrapper
        reply_body = response.choices[0].message.content.strip()
        wrapped_reply = f"✨ Walter Mercado dice: {reply_body}"

        return jsonify({"response": wrapped_reply})

    except Exception as e:
        return jsonify({"response": "Ay, ocurrió un error cósmico. 🌌 Intenta nuevamente.", "error": str(e)}), 500
