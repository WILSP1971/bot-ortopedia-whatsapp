# 🏥 Bot de Ortopedia para WhatsApp

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
source venv/bin/activate  # En Windows: venv\Scripts\activate
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
# bot-ortopedia-whatsapp
