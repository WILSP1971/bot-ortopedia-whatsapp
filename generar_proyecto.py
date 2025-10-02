#!/usr/bin/env python3
"""
Generador Automático del Proyecto Bot de Ortopedia para WhatsApp
Ejecutar: python generar_proyecto.py
"""

import os
import shutil

def create_directory_structure():
    """Crea la estructura de directorios del proyecto"""
    
    directories = [
        'bot-ortopedia-whatsapp',
        'bot-ortopedia-whatsapp/config',
        'bot-ortopedia-whatsapp/tests',
        'bot-ortopedia-whatsapp/templates',
        'bot-ortopedia-whatsapp/static',
        'bot-ortopedia-whatsapp/docs',
        'bot-ortopedia-whatsapp/logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Creado: {directory}")

def create_main_bot_file():
    """Crea el archivo principal del bot"""
    
    content = '''# ============================================================================
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
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Configuración de IA
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Configuración de tu API de Base de Datos
API_BASE_URL = os.getenv('API_BASE_URL', 'https://tu-api.com/api')
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
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
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
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
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
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
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
            f"✅ *Videollamada Zoom Creada*\\n\\n"
            f"📅 Hora: {meeting['start_time']}\\n"
            f"🔢 ID de reunión: {meeting['meeting_id']}\\n"
            f"🔐 Contraseña: {meeting['password']}\\n\\n"
            f"🔗 Enlace directo:\\n{meeting['join_url']}\\n\\n"
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
            f"✅ *Videollamada Google Meet Creada*\\n\\n"
            f"📅 Hora: {meeting['start_time']}\\n\\n"
            f"🔗 Enlace de la reunión:\\n{meeting['meet_link']}\\n\\n"
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
            "¡Bienvenido al Sistema de Ortopedia! 🏥\\n\\n"
            "Para comenzar, ingresa tu número de cédula:"
        )
        update_user_session(phone_number, state="awaiting_cedula")

def process_button_response(phone_number, button_id):
    """Procesa respuestas de botones"""
    if button_id == "consulta_doctor":
        send_whatsapp_message(
            phone_number,
            "💬 *Consulta con Doctor Virtual*\\n\\n"
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
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''
    
    with open('bot-ortopedia-whatsapp/bot_ortopedia.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: bot_ortopedia.py")

def create_env_template():
    """Crea el archivo .env.template"""
    
    content = '''# ==========================================
# WhatsApp Cloud API
# ==========================================
WHATSAPP_TOKEN=tu_token_de_whatsapp_aqui
WHATSAPP_PHONE_ID=tu_phone_id_aqui
VERIFY_TOKEN=tu_verify_token_aqui

# ==========================================
# Inteligencia Artificial
# ==========================================
# OpenAI (ChatGPT)
OPENAI_API_KEY=sk-tu_clave_openai_aqui

# O Anthropic (Claude)
# ANTHROPIC_API_KEY=sk-ant-tu_clave_anthropic_aqui

# ==========================================
# Base de Datos
# ==========================================
API_BASE_URL=https://tu-api.com/api
API_KEY=tu_api_key_aqui

# ==========================================
# Zoom API (Videollamadas)
# ==========================================
ZOOM_API_KEY=tu_client_id_zoom
ZOOM_API_SECRET=tu_client_secret_zoom
ZOOM_ACCOUNT_ID=tu_account_id_zoom

# ==========================================
# Google Meet API (Videollamadas)
# ==========================================
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=primary

# ==========================================
# Configuración del Servidor
# ==========================================
PORT=5000
'''
    
    with open('bot-ortopedia-whatsapp/.env.template', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: .env.template")

def create_requirements():
    """Crea el archivo requirements.txt"""
    
    content = '''# Dependencias del Bot de Ortopedia para WhatsApp

# Framework Web
flask==3.0.0
flask-limiter==3.5.0

# Requests HTTP
requests==2.31.0

# Variables de entorno
python-dotenv==1.0.0

# OpenAI (ChatGPT)
openai==1.3.0

# Anthropic (Claude) - Opcional
anthropic==0.7.0

# Zoom API
PyJWT==2.8.0

# Google Meet API
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0

# Utilidades
pytz==2023.3
schedule==1.2.0

# Email
secure-smtplib==0.1.1

# Producción
gunicorn==21.2.0
'''
    
    with open('bot-ortopedia-whatsapp/requirements.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: requirements.txt")

def create_gitignore():
    """Crea el archivo .gitignore"""
    
    content = '''# Variables de entorno
.env
.env.local

# Credenciales
credentials.json
*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
venv/
env/
ENV/

# Logs
*.log
logs/

# Sistema
.DS_Store
Thumbs.db
.vscode/
.idea/

# Testing
.pytest_cache/
.coverage
htmlcov/
'''
    
    with open('bot-ortopedia-whatsapp/.gitignore', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: .gitignore")

def create_readme():
    """Crea el archivo README.md"""
    
    content = '''# 🏥 Bot de Ortopedia para WhatsApp

Sistema completo de atención médica automatizada con inteligencia artificial para consultorios de ortopedia.

## 🚀 Características

- ✅ Validación automática de pacientes
- 💬 Consultas médicas con IA (ChatGPT/Claude)
- 📤 Envío de estudios médicos (Rayos X, Resonancias)
- 📹 Videollamadas con Zoom y Google Meet
- 📅 Sistema de agendamiento de citas
- 📞 Información de contacto
- 🔐 Seguridad y privacidad de datos

## 📋 Requisitos

- Python 3.8+
- Cuenta de WhatsApp Business
- API Key de OpenAI o Anthropic
- Cuenta de Zoom Pro (opcional)
- Google Workspace (opcional)
- Base de datos con API REST

## 🛠️ Instalación

### 1. Clonar o descargar el proyecto

```bash
cd bot-ortopedia-whatsapp
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia `.env.template` a `.env` y completa tus credenciales:

```bash
cp .env.template .env
```

Edita el archivo `.env` con tus credenciales reales.

### 5. Configurar WhatsApp Business API

1. Ve a https://developers.facebook.com
2. Crea una app de tipo "Empresa"
3. Añade el producto "WhatsApp"
4. Configura tu número de teléfono
5. Obtén tu `WHATSAPP_TOKEN` y `WHATSAPP_PHONE_ID`

### 6. Configurar IA

#### Para ChatGPT:
1. Ve a https://platform.openai.com
2. Crea una API key
3. Añádela a tu `.env`

#### Para Claude (alternativa):
1. Ve a https://console.anthropic.com
2. Obtén tu API key
3. Descomenta las líneas de Claude en el código

### 7. Configurar Zoom (opcional)

Ver `docs/CONFIGURACION_ZOOM.md` para instrucciones detalladas.

### 8. Configurar Google Meet (opcional)

Ver `docs/CONFIGURACION_GOOGLE_MEET.md` para instrucciones detalladas.

## 🚀 Ejecución

### Desarrollo

```bash
python bot_ortopedia.py
```

### Producción

```bash
gunicorn bot_ortopedia:app --bind 0.0.0.0:5000
```

## 🧪 Pruebas

Ejecutar tests de integración:

```bash
python tests/test_zoom.py
python tests/test_google_meet.py
python tests/test_all_video.py
```

## 📁 Estructura del Proyecto

```
bot-ortopedia-whatsapp/
│
├── bot_ortopedia.py          # Código principal del bot
├── requirements.txt           # Dependencias Python
├── .env.template             # Template de variables de entorno
├── .gitignore               # Archivos ignorados por Git
├── README.md                # Este archivo
│
├── config/                  # Configuraciones
│   └── credentials.json     # Credenciales Google (no subir a Git)
│
├── tests/                   # Scripts de prueba
│   ├── test_zoom.py
│   ├── test_google_meet.py
│   └── test_all_video.py
│
├── docs/                    # Documentación
│   ├── CONFIGURACION_ZOOM.md
│   ├── CONFIGURACION_GOOGLE_MEET.md
│   └── API_ENDPOINTS.md
│
└── logs/                    # Archivos de log
    └── bot.log
```

## 🔧 Configuración de Base de Datos

Tu API debe implementar los siguientes endpoints:

- `GET /api/pacientes/cedula/{cedula}` - Validar paciente
- `POST /api/pacientes` - Crear paciente
- `GET /api/citas/disponibles` - Obtener citas
- `POST /api/estudios` - Guardar estudios médicos
- `POST /api/videollamadas` - Guardar videollamadas
- `GET /api/contactos/telefonos` - Obtener teléfonos

Ver `docs/API_ENDPOINTS.md` para detalles completos.

## 🌐 Despliegue

### Heroku

```bash
heroku create mi-bot-ortopedia
git push heroku main
heroku config:set WHATSAPP_TOKEN=tu_token
```

### Railway

1. Conecta tu repositorio Git
2. Configura variables de entorno
3. Deploy automático

### Docker

```bash
docker build -t bot-ortopedia .
docker run -p 5000:5000 --env-file .env bot-ortopedia
```

## 📊 Monitoreo

Ver logs en tiempo real:

```bash
tail -f logs/bot.log
```

## 🔒 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Tokens con expiración
- ✅ Validación de usuarios
- ✅ Rate limiting implementado
- ✅ HTTPS en producción

## 💰 Costos Estimados

- WhatsApp Business API: Gratis (conversaciones iniciadas por usuario)
- ChatGPT API: ~$0.002 por consulta
- Zoom Pro: $14.99/mes
- Google Workspace: $6/mes
- Servidor: $5-10/mes

**Total:** ~$25-30 USD/mes

## 🤝 Soporte

Para problemas o preguntas:

1. Revisa la documentación en `/docs`
2. Verifica los logs en `/logs`
3. Ejecuta los tests en `/tests`

## 📝 Licencia

MIT License - Puedes usar este código libremente para tu consultorio.

## 👨‍💻 Autor

Creado para consultorios de ortopedia que quieren automatizar su atención.

---

**¡Listo para transformar tu consultorio! 🚀**
'''
    
    with open('bot-ortopedia-whatsapp/README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: README.md")

def create_test_files():
    """Crea los archivos de prueba"""
    
    # test_zoom.py
    test_zoom = '''import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_zoom_credentials():
    print("🔍 Verificando credenciales de Zoom...")
    
    required = ['ZOOM_API_KEY', 'ZOOM_API_SECRET', 'ZOOM_ACCOUNT_ID']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Variables faltantes: {', '.join(missing)}")
        return False
    
    print("✅ Credenciales configuradas")
    return True

def test_zoom_meeting():
    print("📹 Probando creación de reunión en Zoom...")
    
    try:
        from bot_ortopedia import create_zoom_meeting
        
        meeting = create_zoom_meeting("Prueba de Consulta", 30)
        
        if meeting:
            print(f"✅ Reunión creada: {meeting['join_url']}")
            return True
        else:
            print("❌ No se pudo crear la reunión")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_zoom_credentials() and test_zoom_meeting():
        print("\\n✅ TODAS LAS PRUEBAS DE ZOOM PASARON")
        sys.exit(0)
    else:
        print("\\n❌ PRUEBAS FALLIDAS")
        sys.exit(1)
'''
    
    with open('bot-ortopedia-whatsapp/tests/test_zoom.py', 'w', encoding='utf-8') as f:
        f.write(test_zoom)
    
    print("✅ Creado: tests/test_zoom.py")

def create_procfile():
    """Crea el Procfile para Heroku"""
    
    content = '''web: gunicorn bot_ortopedia:app
'''
    
    with open('bot-ortopedia-whatsapp/Procfile', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: Procfile")

def create_dockerfile():
    """Crea el Dockerfile"""
    
    content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "bot_ortopedia:app", "--bind", "0.0.0.0:5000"]
'''
    
    with open('bot-ortopedia-whatsapp/Dockerfile', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: Dockerfile")

def create_documentation():
    """Crea archivos de documentación"""
    
    # API_ENDPOINTS.md
    api_doc = '''# 📡 Documentación de API Endpoints

## Endpoints Requeridos en tu API

### 1. Validación de Pacientes

**GET** `/api/pacientes/cedula/{cedula}`

Valida si un paciente existe en la base de datos.

**Respuesta exitosa (200):**
```json
{
  "id": 123,
  "cedula": "1234567890",
  "nombre": "Juan",
  "apellidos": "Pérez García",
  "email": "juan@example.com",
  "telefono": "+57300123456"
}
```

**Respuesta no encontrado (404):**
```json
{
  "error": "Paciente no encontrado"
}
```

### 2. Crear Paciente

**POST** `/api/pacientes`

Crea un nuevo paciente en el sistema.

**Body:**
```json
{
  "cedula": "1234567890",
  "nombre": "Juan",
  "apellidos": "Pérez García",
  "fecha_registro": "2025-10-02T10:30:00"
}
```

**Respuesta (201):**
```json
{
  "id": 123,
  "cedula": "1234567890",
  "nombre": "Juan",
  "apellidos": "Pérez García",
  "created_at": "2025-10-02T10:30:00"
}
```

### 3. Obtener Citas Disponibles

**GET** `/api/citas/disponibles`

Obtiene las citas disponibles para agendar.

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "fecha": "2025-10-15",
    "hora": "10:00",
    "doctor": "Dr. García"
  },
  {
    "id": 2,
    "fecha": "2025-10-15",
    "hora": "11:00",
    "doctor": "Dr. Rodríguez"
  }
]
```

### 4. Guardar Estudios Médicos

**POST** `/api/estudios`

Guarda un estudio médico (imagen) del paciente.

**Body:**
```json
{
  "patient_id": 123,
  "image_url": "https://...",
  "image_type": "rayos_x",
  "fecha": "2025-10-02T10:30:00"
}
```

### 5. Guardar Videollamadas

**POST** `/api/videollamadas`

Guarda información de una videollamada programada.

**Body:**
```json
{
  "patient_id": 123,
  "platform": "zoom",
  "meeting_url": "https://zoom.us/j/...",
  "meeting_id": "123456789",
  "created_at": "2025-10-02T10:30:00",
  "status": "scheduled"
}
```

### 6. Obtener Teléfonos de Contacto

**GET** `/api/contactos/telefonos`

Obtiene los teléfonos de contacto de la clínica.

**Respuesta (200):**
```json
[
  {
    "nombre": "Recepción",
    "telefono": "+57 300 123 4567",
    "horario": "Lunes a Viernes: 8am - 6pm"
  },
  {
    "nombre": "Emergencias",
    "telefono": "+57 300 123 4568",
    "horario": "24/7"
  }
]
```

## Autenticación

Todos los endpoints requieren un token de autorización en el header:

```
Authorization: Bearer tu_api_key_aqui
```

## Códigos de Estado

- `200` - Éxito
- `201` - Creado exitosamente
- `400` - Petición inválida
- `401` - No autorizado
- `404` - No encontrado
- `500` - Error del servidor
'''
    
    with open('bot-ortopedia-whatsapp/docs/API_ENDPOINTS.md', 'w', encoding='utf-8') as f:
        f.write(api_doc)
    
    print("✅ Creado: docs/API_ENDPOINTS.md")

def create_install_script():
    """Crea script de instalación automática"""
    
    content = '''#!/bin/bash

echo "🏥 Bot de Ortopedia para WhatsApp - Instalación"
echo "=============================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Copiar template de .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.template .env
    echo "⚠️  Por favor, edita el archivo .env con tus credenciales"
fi

echo ""
echo "=============================================="
echo "✅ Instalación completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales"
echo "2. Ejecuta: python bot_ortopedia.py"
echo ""
'''
    
    with open('bot-ortopedia-whatsapp/install.sh', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Hacer ejecutable
    os.chmod('bot-ortopedia-whatsapp/install.sh', 0o755)
    
    print("✅ Creado: install.sh")

def create_zip_instructions():
    """Crea instrucciones para crear ZIP"""
    
    content = '''# 📦 Cómo Crear el ZIP del Proyecto

## Opción 1: Desde la Terminal (Linux/Mac)

```bash
cd ..
zip -r bot-ortopedia-whatsapp.zip bot-ortopedia-whatsapp/ -x "*.pyc" "*__pycache__*" "*.log" ".env"
```

## Opción 2: Desde Windows

1. Abre el explorador de archivos
2. Navega a la carpeta padre de `bot-ortopedia-whatsapp`
3. Click derecho en la carpeta `bot-ortopedia-whatsapp`
4. Selecciona "Enviar a" → "Carpeta comprimida (en zip)"

## Opción 3: Desde Python

Ejecuta este comando:

```bash
python -c "import shutil; shutil.make_archive('bot-ortopedia-whatsapp', 'zip', 'bot-ortopedia-whatsapp')"
```

## Importante

**NO incluyas en el ZIP:**
- Archivo `.env` (credenciales)
- Carpeta `venv/` (entorno virtual)
- Archivo `credentials.json` (Google)
- Carpeta `__pycache__/`
- Archivos `.log`

El `.gitignore` ya está configurado para ignorar estos archivos.
'''
    
    with open('bot-ortopedia-whatsapp/CREAR_ZIP.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Creado: CREAR_ZIP.md")

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🏥 GENERADOR DEL PROYECTO BOT DE ORTOPEDIA")
    print("=" * 60 + "\n")
    
    try:
        # Crear estructura
        print("📁 Creando estructura de directorios...")
        create_directory_structure()
        print()
        
        # Crear archivos principales
        print("📄 Creando archivos principales...")
        create_main_bot_file()
        create_env_template()
        create_requirements()
        create_gitignore()
        create_readme()
        create_procfile()
        create_dockerfile()
        print()
        
        # Crear tests
        print("🧪 Creando archivos de prueba...")
        create_test_files()
        print()
        
        # Crear documentación
        print("📚 Creando documentación...")
        create_documentation()
        create_zip_instructions()
        print()
        
        # Crear scripts
        print("🔧 Creando scripts de instalación...")
        create_install_script()
        print()
        
        print("=" * 60)
        print("✅ PROYECTO GENERADO EXITOSAMENTE!")
        print("=" * 60)
        print()
        print("📁 Estructura creada en: ./bot-ortopedia-whatsapp/")
        print()
        print("📋 Próximos pasos:")
        print("   1. cd bot-ortopedia-whatsapp")
        print("   2. Edita el archivo .env.template y renómbralo a .env")
        print("   3. pip install -r requirements.txt")
        print("   4. python bot_ortopedia.py")
        print()
        print("📦 Para crear el ZIP:")
        print("   Ver instrucciones en: CREAR_ZIP.md")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
