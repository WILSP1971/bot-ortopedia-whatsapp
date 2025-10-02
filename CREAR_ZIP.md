# 📦 Cómo Crear el ZIP del Proyecto

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
