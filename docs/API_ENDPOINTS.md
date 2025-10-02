# 📡 Documentación de API Endpoints

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
