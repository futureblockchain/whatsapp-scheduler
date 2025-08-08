# 📱 WhatsApp Scheduler

Una aplicación full-stack para programar mensajes de WhatsApp con envío automático.

## 🚀 Características

- ✅ **Programar mensajes** para envío futuro
- ✅ **Dashboard** con estadísticas en tiempo real  
- ✅ **Gestión completa** (crear, editar, eliminar mensajes)
- ✅ **Envío inmediato** para testing
- ✅ **Filtros y búsqueda** avanzada
- ✅ **Interfaz responsive** con TailwindCSS
- ✅ **API REST** completa con FastAPI
- ✅ **Programador automático** con APScheduler
- ✅ **Base de datos** SQLite/PostgreSQL
- ✅ **Migraciones** con Alembic

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno para Python
- **SQLAlchemy** - ORM para base de datos
- **Alembic** - Migraciones de base de datos
- **APScheduler** - Programador de tareas
- **PostgreSQL/SQLite** - Base de datos
- **Pydantic** - Validación de datos

### Frontend
- **React 18** - Librería de UI
- **Vite** - Build tool rápido
- **TailwindCSS** - Framework de CSS utility-first
- **React Hook Form** - Manejo de formularios
- **Axios** - Cliente HTTP
- **React Hot Toast** - Notificaciones
- **Lucide React** - Iconos

## 📁 Estructura del Proyecto

```
whatsapp-scheduler/
├── backend/                 # Código del servidor
│   ├── main.py             # FastAPI app principal
│   ├── models.py           # Modelos de SQLAlchemy
│   ├── schemas.py          # Schemas de Pydantic
│   ├── database.py         # Configuración de BD
│   ├── settings.py         # Variables de entorno
│   ├── scheduler.py        # APScheduler service
│   ├── whatsapp_service.py # Servicio de WhatsApp
│   ├── requirements.txt    # Dependencias Python
│   ├── .env               # Variables de entorno
│   └── alembic/           # Migraciones
│       ├── env.py
│       └── versions/
├── frontend/               # Código del cliente
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CreateMessage.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageDetails.jsx
│   │   │   └── TestMessage.jsx
│   │   ├── App.jsx        # Componente principal
│   │   ├── main.jsx       # Punto de entrada
│   │   ├── api.js         # Cliente API
│   │   └── index.css      # Estilos CSS
│   ├── package.json       # Dependencias Node.js
│   ├── vite.config.js     # Configuración Vite
│   ├── tailwind.config.js # Configuración Tailwind
│   └── index.html         # HTML base
└── README.md              # Esta documentación
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Node.js 18+
- npm o yarn

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd whatsapp-scheduler
```

### 2. Configurar el Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Configurar Variables de Entorno

Edita el archivo `.env` con tus configuraciones:

```env
# Base de datos (SQLite por defecto para desarrollo)
DATABASE_URL=sqlite:///./whatsapp_scheduler.db

# Para PostgreSQL:
# DATABASE_URL=postgresql://usuario:password@localhost:5432/whatsapp_scheduler

# WhatsApp Cloud API (opcional para desarrollo)
WHATSAPP_ACCESS_TOKEN=tu_access_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id

# Configuración de la app
DEBUG=true
SECRET_KEY=tu-clave-secreta-super-segura
```

### 4. Inicializar Base de Datos

```bash
# Inicializar Alembic
alembic init alembic

# Crear primera migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 5. Configurar el Frontend

```bash
# En una nueva terminal, navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Crear archivo de configuración (opcional)
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

## 🏃‍♂️ Ejecutar la Aplicación

### Opción 1: Ejecutar por separado

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Servidor corriendo en http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Aplicación corriendo en http://localhost:5173
```

### Opción 2: Script de desarrollo (crear este archivo)

Crear `run_dev.sh`:
```bash
#!/bin/bash
# Ejecutar backend en segundo plano
cd backend && python main.py &
BACKEND_PID=$!

# Ejecutar frontend
cd frontend && npm run dev &
FRONTEND_PID=$!

# Esperar y limpiar al salir
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

## 🔧 Configuración de WhatsApp

### Para usar WhatsApp Cloud API (Producción):

1. **Crear una aplicación en Meta for Developers:**
   - Ve a https://developers.facebook.com/
   - Crear nueva app > Tipo "Business"
   - Agregar producto "WhatsApp Business API"

2. **Obtener credenciales:**
   - `WHATSAPP_ACCESS_TOKEN`: Token de acceso de la app
   - `WHATSAPP_PHONE_NUMBER_ID`: ID del número de teléfono

3. **Actualizar .env:**
   ```env
   WHATSAPP_ACCESS_TOKEN=tu_token_real
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_id_real
   ```

### Para desarrollo (Simulación):

Si no tienes acceso a la API de WhatsApp, la aplicación funciona en modo simulación:
- Los mensajes se "envían" pero solo se muestran en la consola
- Perfecto para desarrollo y testing

## 📊 API Endpoints

### Mensajes Programados
- `POST /api/schedule` - Crear mensaje programado
- `GET /api/scheduled` - Listar mensajes con filtros
- `GET /api/scheduled/{id}` - Obtener mensaje específico  
- `PUT /api/scheduled/{id}` - Actualizar mensaje
- `DELETE /api/scheduled/{id}` - Eliminar mensaje

### Testing
- `POST /api/send-now` - Enviar mensaje inmediatamente

### Sistema
- `GET /` - Estado de la API
- `GET /api/stats` - Estadísticas del sistema

### Ejemplos de uso:

```bash
# Crear mensaje programado
curl -X POST "http://localhost:8000/api/schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5255123456789",
    "message": "Hola, este es un mensaje programado",
    "send_time": "2024-12-01T10:00:00"
  }'

# Listar mensajes
curl "http://localhost:8000/api/scheduled?status=pending&page=1&per_page=10"

# Enviar mensaje inmediatamente  
curl -X POST "http://localhost:8000/api/send-now" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5255123456789", 
    "message": "Mensaje de prueba"
  }'
```

## 🗄️ Cambiar de SQLite a PostgreSQL

1. **Instalar PostgreSQL** y crear base de datos:
   ```sql
   CREATE DATABASE whatsapp_scheduler;
   CREATE USER whatsapp_user WITH PASSWORD 'tu_password';
   GRANT ALL PRIVILEGES ON DATABASE whatsapp_scheduler TO whatsapp_user;
   ```

2. **Actualizar .env:**
   ```env
   DATABASE_URL=postgresql://whatsapp_user:tu_password@localhost:5432/whatsapp_scheduler
   ```

3. **Ejecutar migraciones:**
   ```bash
   alembic upgrade head
   ```

## 🚀 Despliegue en Producción

### Backend (Railway/Render/DigitalOcean):

1. **Configurar variables de entorno en la plataforma**
2. **Usar PostgreSQL como base de datos**
3. **Configurar el archivo de requirements.txt**
4. **Comando de inicio:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify):

1. **Build command:** `npm run build`
2. **Output directory:** `dist`
3. **Configurar variable de entorno:** `VITE_API_URL=https://tu-api.com`

### Ejemplo para Railway:

**railway.toml:**
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "always"
```

## 🛠️ Desarrollo

### Comandos útiles:

```bash
# Backend
pip install -r requirements.txt  # Instalar dependencias
alembic revision --autogenerate -m "descripcion"  # Nueva migración
alembic upgrade head  # Aplicar migraciones
python main.py  # Ejecutar servidor

# Frontend  
npm install          # Instalar dependencias
npm run dev         # Servidor de desarrollo
npm run build       # Build para producción
npm run preview     # Preview del build
```

### Estructura de componentes:

- **Dashboard**: Estadísticas y resumen
- **CreateMessage**: Formulario para nuevos mensajes
- **MessageList**: Lista con filtros y paginación  
- **MessageDetails**: Ver/editar mensaje específico
- **TestMessage**: Envío inmediato para pruebas

## 🐛 Solución de Problemas

### El scheduler no envía mensajes:
- Verificar que APScheduler esté iniciado
- Revisar logs del backend
- Verificar configuración de zona horaria

### Errores de CORS:
- Verificar `ALLOWED_ORIGINS` en settings.py
- Asegurar que el proxy de Vite esté configurado

### Base de datos:
- SQLite: Verificar permisos de archivo
- PostgreSQL: Verificar conexión y credenciales

### WhatsApp API:
- Verificar tokens de acceso
- Revisar límites de rate limiting
- Modo simulación siempre funciona

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request


**¡Hecho con amor para automatizar tus mensajes de WhatsApp!**