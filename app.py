# ============================================================================
# BOT DE ORTOPEDIA PARA WHATSAPP - SISTEMA COMPLETO
# ============================================================================

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import openai  # Para ChatGPT
# from anthropic import Anthropic  # Para Claude (alternativa)

# Librerías para videollamadas
import jwt
import time
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

app = Flask(__name__)

# Configuración de WhatsApp Cloud API
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')
VERIFY_TOKEN = "TWSCodeJG#75" #os.getenv('VERIFY_TOKEN')

# Configuración de IA
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Configuración de tu API de Base de Datos
API_BASE_URL = os.getenv('API_BASE_URL', 'https://appsintranet.esculapiosis.com/ApiCampbell/api')
API_KEY = os.getenv('API_KEY')

# Configuración de Zoom API
ZOOM_API_KEY = os.getenv('ZOOM_API_KEY')
ZOOM_API_SECRET = os.getenv('ZOOM_API_SECRET')
ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')

# Configuración de Google Meet API
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

# Almacenamiento temporal de sesiones de usuario
user_sessions = {}

# ============================================================================
# FUNCIONES DE WHATSAPP API
# ============================================================================

def send_whatsapp_message(phone_number, message):
    """Envía un mensaje de texto por WhatsApp"""
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def send_whatsapp_interactive_buttons(phone_number, body_text, buttons):
    """Envía mensaje con botones interactivos"""
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    buttons_list = []
    for btn in buttons:
        buttons_list.append({
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"]
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons_list}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def send_whatsapp_list(phone_number, body_text, button_text, sections):
    """Envía mensaje con lista de opciones"""
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ============================================================================
# FUNCIONES DE BASE DE DATOS (API)
# ============================================================================

def validate_cedula(cedula):
    """Valida si la cédula existe en la base de datos"""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{API_BASE_URL}/pacientes/cedula/{cedula}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error validando cédula: {e}")
        return None

def create_patient(cedula, nombre, apellidos):
    """Crea un nuevo paciente en la base de datos"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "cedula": cedula,
            "nombre": nombre,
            "apellidos": apellidos,
            "fecha_registro": datetime.now().isoformat()
        }
        response = requests.post(
            f"{API_BASE_URL}/pacientes",
            headers=headers,
            json=data,
            timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"Error creando paciente: {e}")
        return None

def get_appointments():
    """Obtiene las citas disponibles"""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{API_BASE_URL}/citas/disponibles",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error obteniendo citas: {e}")
        return []

def get_contact_phones():
    """Obtiene los teléfonos de contacto"""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{API_BASE_URL}/contactos/telefonos",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error obteniendo teléfonos: {e}")
        return []

def save_medical_image(patient_id, image_url, image_type):
    """Guarda una imagen médica en la base de datos"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "patient_id": patient_id,
            "image_url": image_url,
            "image_type": image_type,
            "fecha": datetime.now().isoformat()
        }
        response = requests.post(
            f"{API_BASE_URL}/estudios",
            headers=headers,
            json=data,
            timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"Error guardando imagen: {e}")
        return None

# ============================================================================
# FUNCIONES DE IA (CHATGPT/CLAUDE)
# ============================================================================

def get_ai_response(question, context="ortopedia"):
    """Obtiene respuesta de IA especializada en ortopedia"""
    try:
        system_prompt = """Eres un asistente médico especializado en ortopedia.
        Proporciona respuestas precisas, profesionales y basadas en evidencia médica.
        Si la pregunta está fuera de tu especialidad, indícalo claramente.
        Siempre recomienda consultar con un médico para diagnósticos definitivos."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error con IA: {e}")
        return "Disculpa, no puedo procesar tu consulta en este momento."

# ============================================================================
# FUNCIONES DE ZOOM API
# ============================================================================

def create_zoom_meeting(topic, duration=60, start_time=None):
    """Crea una reunión en Zoom"""
    try:
        import base64
        
        token_url = "https://zoom.us/oauth/token"
        token_data = {
            "grant_type": "account_credentials",
            "account_id": ZOOM_ACCOUNT_ID
        }
        
        auth_string = f"{ZOOM_API_KEY}:{ZOOM_API_SECRET}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        token_headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        
        if token_response.status_code != 200:
            return None
        
        access_token = token_response.json()['access_token']
        
        url = "https://api.zoom.us/v2/users/me/meetings"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        if not start_time:
            start_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
        
        meeting_data = {
            "topic": topic,
            "type": 2,
            "start_time": start_time,
            "duration": duration,
            "timezone": "America/Bogota",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": True,
                "mute_upon_entry": False,
                "watermark": False,
                "audio": "both",
                "auto_recording": "none",
                "waiting_room": False
            }
        }
        
        response = requests.post(url, headers=headers, json=meeting_data)
        
        if response.status_code == 201:
            meeting_info = response.json()
            return {
                "platform": "zoom",
                "join_url": meeting_info['join_url'],
                "meeting_id": meeting_info['id'],
                "password": meeting_info.get('password', 'Sin contraseña'),
                "start_time": meeting_info['start_time']
            }
        return None
            
    except Exception as e:
        print(f"Error en create_zoom_meeting: {e}")
        return None

# ============================================================================
# FUNCIONES DE GOOGLE MEET API
# ============================================================================

def get_google_calendar_service():
    """Crea y retorna el servicio de Google Calendar"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error obteniendo servicio Google Calendar: {e}")
        return None

def create_google_meet_meeting(summary, duration=60, start_time=None, attendee_email=None):
    """Crea una reunión de Google Meet"""
    try:
        service = get_google_calendar_service()
        
        if not service:
            return None
        
        if not start_time:
            start_time = datetime.now() + timedelta(minutes=5)
        
        end_time = start_time + timedelta(minutes=duration)
        
        event = {
            'summary': summary,
            'description': 'Consulta médica de ortopedia por videollamada',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Bogota',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Bogota',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{int(time.time())}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'attendees': [],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        if attendee_email:
            event['attendees'].append({'email': attendee_email})
        
        event = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        meet_link = event.get('hangoutLink')
        
        if not meet_link:
            conference_data = event.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    meet_link = entry.get('uri')
                    break
        
        return {
            "platform": "google_meet",
            "meet_link": meet_link,
            "event_id": event['id'],
            "start_time": event['start']['dateTime'],
            "calendar_link": event.get('htmlLink')
        }
        
    except HttpError as error:
        print(f"Error de Google API: {error}")
        return None
    except Exception as e:
        print(f"Error en create_google_meet_meeting: {e}")
        return None

def save_video_call_info(patient_id, platform, meeting_url, meeting_id):
    """Guarda la información de la videollamada en la base de datos"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "patient_id": patient_id,
            "platform": platform,
            "meeting_url": meeting_url,
            "meeting_id": meeting_id,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        response = requests.post(
            f"{API_BASE_URL}/videollamadas",
            headers=headers,
            json=data,
            timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"Error guardando videollamada: {e}")
        return None

# ============================================================================
# GESTIÓN DE SESIONES
# ============================================================================

def get_user_session(phone_number):
    """Obtiene o crea una sesión de usuario"""
    if phone_number not in user_sessions:
        user_sessions[phone_number] = {
            "state": "initial",
            "data": {},
            "conversation_history": []
        }
    return user_sessions[phone_number]

def update_user_session(phone_number, state=None, data=None):
    """Actualiza la sesión del usuario"""
    session = get_user_session(phone_number)
    if state:
        session["state"] = state
    if data:
        session["data"].update(data)

# ============================================================================
# MENÚ Y NAVEGACIÓN
# ============================================================================

def show_main_menu(phone_number):
    """Muestra el menú principal"""
    sections = [{
        "title": "Servicios Disponibles",
        "rows": [
            {
                "id": "consultas",
                "title": "📋 Manejo de Consultas",
                "description": "Consultas médicas y envío de estudios"
            },
            {
                "id": "citas",
                "title": "📅 Agendar Citas",
                "description": "Ver y agendar citas disponibles"
            },
            {
                "id": "telefonos",
                "title": "📞 Teléfonos de Atención",
                "description": "Información de contacto"
            }
        ]
    }]
    
    send_whatsapp_list(
        phone_number,
        "Selecciona el servicio que necesitas:",
        "Ver opciones",
        sections
    )

def handle_medical_consultation(phone_number):
    """Maneja el menú de consultas médicas"""
    buttons = [
        {"id": "consulta_doctor", "title": "💬 Consultar Doctor"},
        {"id": "enviar_estudio", "title": "📤 Enviar Estudio"},
        {"id": "videollamada", "title": "📹 Videollamada"}
    ]
    
    send_whatsapp_interactive_buttons(
        phone_number,
        "¿Qué necesitas en el área de consultas?",
        buttons
    )
    update_user_session(phone_number, state="consultas_menu")

def initiate_video_call(phone_number):
    """Inicia una videollamada con opciones de Zoom o Google Meet"""
    buttons = [
        {"id": "video_zoom", "title": "📹 Zoom"},
        {"id": "video_meet", "title": "🎥 Google Meet"}
    ]
    
    send_whatsapp_interactive_buttons(
        phone_number,
        "Selecciona la plataforma para tu videollamada:",
        buttons
    )
    update_user_session(phone_number, state="selecting_video_platform")

def handle_video_call_zoom(phone_number):
    """Maneja la creación de videollamada por Zoom"""
    session = get_user_session(phone_number)
    patient_data = session["data"]
    patient_name = patient_data.get("nombre", "Paciente")
    
    send_whatsapp_message(phone_number, "📹 Creando tu sala de Zoom...")
    
    meeting_topic = f"Consulta Ortopedia - {patient_name}"
    meeting = create_zoom_meeting(topic=meeting_topic, duration=30)
    
    if meeting:
        message = (
            f"✅ *Videollamada Zoom Creada*\n\n"
            f"📅 Hora: {meeting['start_time']}\n"
            f"🔢 ID de reunión: {meeting['meeting_id']}\n"
            f"🔐 Contraseña: {meeting['password']}\n\n"
            f"🔗 Enlace directo:\n{meeting['join_url']}\n\n"
            f"💡 Puedes unirte 5 minutos antes de la hora programada."
        )
        send_whatsapp_message(phone_number, message)
        
        save_video_call_info(
            patient_data.get("patient_id"),
            "zoom",
            meeting['join_url'],
            meeting['meeting_id']
        )
    else:
        send_whatsapp_message(
            phone_number,
            "❌ No pudimos crear la videollamada de Zoom. Contacta con soporte."
        )

def handle_video_call_meet(phone_number):
    """Maneja la creación de videollamada por Google Meet"""
    session = get_user_session(phone_number)
    patient_data = session["data"]
    patient_name = patient_data.get("nombre", "Paciente")
    
    send_whatsapp_message(phone_number, "🎥 Creando tu sala de Google Meet...")
    
    meeting_summary = f"Consulta Ortopedia - {patient_name}"
    meeting = create_google_meet_meeting(summary=meeting_summary, duration=30)
    
    if meeting:
        message = (
            f"✅ *Videollamada Google Meet Creada*\n\n"
            f"📅 Hora: {meeting['start_time']}\n\n"
            f"🔗 Enlace de la reunión:\n{meeting['meet_link']}\n\n"
            f"💡 Puedes unirte en cualquier momento usando el enlace."
        )
        send_whatsapp_message(phone_number, message)
        
        save_video_call_info(
            patient_data.get("patient_id"),
            "google_meet",
            meeting['meet_link'],
            meeting['event_id']
        )
    else:
        send_whatsapp_message(
            phone_number,
            "❌ No pudimos crear la videollamada de Google Meet. Contacta con soporte."
        )

# ============================================================================
# WEBHOOK
# ============================================================================

@app.get("/")
def root():
    return {"ok": True, "msg": "WhatsApp backend running."}

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verifica el webhook de WhatsApp"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe mensajes de WhatsApp"""
    data = request.get_json()
    
    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' not in value:
            return jsonify({"status": "ok"}), 200
        
        message = value['messages'][0]
        phone_number = message['from']
        message_type = message['type']
        
        if message_type == 'text':
            text = message['text']['body'].lower().strip()
            process_text_message(phone_number, text)
            
        elif message_type == 'interactive':
            interactive = message['interactive']
            if interactive['type'] == 'button_reply':
                button_id = interactive['button_reply']['id']
                process_button_response(phone_number, button_id)
            elif interactive['type'] == 'list_reply':
                list_id = interactive['list_reply']['id']
                process_list_response(phone_number, list_id)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error"}), 500

def process_text_message(phone_number, text):
    """Procesa mensajes de texto"""
    session = get_user_session(phone_number)
    state = session["state"]
    
    if text in ['menu', 'menú', 'inicio']:
        show_main_menu(phone_number)
        update_user_session(phone_number, state="main_menu")
        return
    
    if state == "initial":
        send_whatsapp_message(
            phone_number,
            "¡Bienvenido al Sistema de Ortopedia! 🏥\n\n"
            "Para comenzar, ingresa tu número de cédula:"
        )
        update_user_session(phone_number, state="awaiting_cedula")

def process_button_response(phone_number, button_id):
    """Procesa respuestas de botones"""
    if button_id == "consulta_doctor":
        send_whatsapp_message(
            phone_number,
            "💬 *Consulta con Doctor Virtual*\n\n"
            "Hazme cualquier pregunta sobre ortopedia."
        )
        update_user_session(phone_number, state="doctor_chat")
        
    elif button_id == "videollamada":
        initiate_video_call(phone_number)
    
    elif button_id == "video_zoom":
        handle_video_call_zoom(phone_number)
    
    elif button_id == "video_meet":
        handle_video_call_meet(phone_number)

def process_list_response(phone_number, list_id):
    """Procesa respuestas de listas"""
    if list_id == "consultas":
        handle_medical_consultation(phone_number)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)
    app.run(debug=True)
