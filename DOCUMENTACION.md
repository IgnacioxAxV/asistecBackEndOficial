# Documentación Completa - API Asistec

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Configuración Inicial](#configuración-inicial)
5. [Estructura de Carpetas](#estructura-de-carpetas)
6. [Modelo de Datos](#modelo-de-datos)
7. [Autenticación](#autenticación)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Flujos Principales](#flujos-principales)
10. [Patrones de Código](#patrones-de-código)
11. [Gestión de Errores](#gestión-de-errores)
12. [Desarrollo y Despliegue](#desarrollo-y-despliegue)

---

## Descripción General

**Asistec** es una API REST construida con FastAPI que funciona como un sistema de gestión de comunidades académicas. Permite:

- **Gestión de Usuarios**: Registro, autenticación y perfiles de estudiantes
- **Canales de Comunicación**: Espacios de colaboración por áreas académicas
- **Contenido**: Posts, eventos, cursos y actividades
- **Suscripciones**: Asociación de usuarios con canales y contenido
- **Profesorado**: Gestión de profesores y cursos

La plataforma está diseñada para estudiantes del Tecnológico de Costa Rica (TEC) con validación de dominios de correo institucionales.

---

## Arquitectura del Proyecto

La arquitectura sigue el patrón **MVC (Model-View-Controller)** con separación de responsabilidades:

```
FastAPI Application
    ├── Routes (Entrada de peticiones HTTP)
    ├── Controllers (Lógica de negocio)
    ├── Models (ORM - SQLAlchemy)
    ├── Schemas (Validación Pydantic)
    └── Database (Conexión PostgreSQL)
```

### Flujo de una Solicitud

```
HTTP Request
    ↓
Route Handler (routes/*.py)
    ↓
Controller Function (controllers/*.py)
    ↓
Model Query (models/*.py)
    ↓
Database (PostgreSQL)
    ↓
HTTP Response (Pydantic Schema)
```

---

## Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Framework | FastAPI | 0.115.8 |
| ORM | SQLAlchemy | 2.0.38 |
| Base de Datos | PostgreSQL | - |
| Servidor | Uvicorn | 0.34.0 |
| Validación | Pydantic | 2.10.6 |
| Seguridad | Bcrypt | 4.3.0 |
| Testing | Pytest | 8.3.5 |
| Python | - | 3.9+ |

---

## Configuración Inicial

### 1. Requisitos Previos

- Python 3.9+
- PostgreSQL 12+
- pip (gestor de paquetes)
- Docker (opcional, para contenedores)

### 2. Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv asistec

# Activar entorno
source asistec/bin/activate  # macOS/Linux
# o
asistec\Scripts\activate  # Windows

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=asistec
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Inicializar Base de Datos

```bash
# Las tablas se crean automáticamente al ejecutar app.py
# La primera ejecución también inserta datos iniciales de áreas
python -m uvicorn app:app --reload
```

---

## Estructura de Carpetas

```
asistecBackEnd/
├── app.py                    # Punto de entrada principal
├── run_server.py             # Script para ejecutar servidor con Uvicorn
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno (NO COMMITEAR)
├── .env.example              # Plantilla de variables
│
├── models/                   # ORM - Definición de entidades
│   ├── __init__.py
│   ├── Users.py              # Modelo de usuario
│   ├── Areas.py              # Modelo de área académica
│   ├── Channels.py           # Modelo de canal de comunicación
│   ├── Courses.py            # Modelo de curso
│   ├── Events.py             # Modelo de evento
│   ├── Posts.py              # Modelo de publicación
│   ├── Professors.py         # Modelo de profesor
│   ├── ProfessorAreas.py     # Modelo de relación profesor-área (N:M)
│   ├── Subscriptions.py      # Modelo de suscripción
│   └── Activities.py         # Modelo de actividad
│
├── schemas/                  # Pydantic - Validación de entrada/salida
│   ├── __init__.py
│   ├── users_schemas.py
│   ├── areas_schemas.py
│   ├── channels_schemas.py
│   ├── courses_schemas.py
│   ├── events_schemas.py
│   ├── posts_schemas.py
│   ├── professors_schemas.py
│   ├── subscriptions_schemas.py
│   └── activities_schemas.py
│
├── controllers/              # Lógica de negocio
│   ├── __init__.py
│   ├── users_controllers.py
│   ├── areas_controllers.py
│   ├── channels_controllers.py
│   ├── courses_controllers.py
│   ├── events_controllers.py
│   ├── posts_controllers.py
│   ├── professors_controllers.py
│   ├── subscription_controllers.py
│   └── activities_controllers.py
│
├── routes/                   # Endpoints HTTP
│   ├── __init__.py           # Agregador de todos los routers
│   ├── users_routes.py
│   ├── areas_routes.py
│   ├── channels_routes.py
│   ├── courses_routes.py
│   ├── events_routes.py
│   ├── posts_routes.py
│   ├── professors_routes.py
│   ├── subscriptions_routes.py
│   └── activities_routes.py
│
├── database/                 # Configuración de BD
│   ├── __init__.py           # Exporta engine, SessionLocal, get_db
│   └── db_config.py          # Configuración SQLAlchemy
│
├── interfaces/               # Patrones de diseño
│   ├── __init__.py
│   ├── auth_factory.py       # Factory para proveedores de auth
│   └── auth_provider.py      # Interfaz base de autenticación
│
└── tests/                    # Tests automatizados
    ├── __init__.py
    └── test_user-channel_subscription.py
```

---

## Modelo de Datos

### Diagrama Entidad-Relación

```
Areas (1) ──────────────── (N) Users
  │                          │
  │                          ├─── (N) Posts
  │                          ├─── (N) Events
  │                          ├─── (N) Courses ──── (N:1) Professors
  │                          ├─── (N) Activities
  │                          └─── (N) Subscriptions
  │                                     │
  ├─ (1) Channels ──────────────────────┘
  │      │
  │      └─── (N) Posts
  │
  └─ (N) ProfessorAreas ──── (N) Professors
         (tabla intermedia N:M)
```

### Descripción de Entidades

#### 1. **Users** (Usuarios)

Representa a los estudiantes de la plataforma.

```python
- user_id (PK)              # ID único
- name                      # Nombre
- lastname                  # Apellido
- mail                      # Email único (dominio TEC)
- password                  # Contraseña hasheada (bcrypt)
- carnet_number             # Número de carné (único)
- gender                    # Género (M/F/Otro)
- birth_date                # Fecha de nacimiento
- area_id (FK)              # Área académica
- is_active                 # Estado del usuario
- last_login                # Último login
- user_type                 # Tipo de usuario (1=estudiante, etc.)
```

**Relaciones:**
- Pertenece a una `Area`
- Puede tener múltiples `Subscriptions` a canales
- Puede crear múltiples `Posts`
- Puede crear múltiples `Events`
- Puede inscribirse en múltiples `Courses`
- Puede realizar múltiples `Activities`

#### 2. **Areas** (Áreas Académicas)

Divide la institución en secciones académicas.

```python
- area_id (PK)              # ID único
- area_name                 # Nombre del área
- is_major                  # True = carrera, False = otra área
```

**Datos Iniciales (insertados automáticamente):**
- DEVESA (False)
- Escuela Ciencias Naturales y Exactas San Carlos (False)
- Escuela de Ciencias del Lenguaje San Carlos (False)
- Dirección de Campus Tecnológico Local San Carlos (False)
- Ing. En Computación San Carlos (True)
- Ing. Electrónica San Carlos (True)
- Ing. Producción Industrial San Carlos (True)
- Ing. Agronomía San Carlos (True)
- Administración de Empresas San Carlos (True)
- Gestión del Turismo Rural Sostenible San Carlos (True)
- Gestión en Sostenibilidad Turística Sostenible San Carlos (True)

#### 3. **Channels** (Canales de Comunicación)

Espacios de colaboración por área.

```python
- channel_id (PK)           # ID único
- channel_name              # Nombre del canal
- area_id (FK)              # Área a la que pertenece
```

**Relaciones:**
- Pertenece a una `Area`
- Tiene múltiples `Subscriptions` de usuarios
- Contiene múltiples `Posts`

#### 4. **Subscriptions** (Suscripciones)

Asociación entre usuarios y canales.

```python
- subscription_id (PK)      # ID único
- user_id (FK)              # Usuario suscrito
- channel_id (FK)           # Canal
- is_admin                  # True = administrador del canal
- is_subscribed             # True = suscripción activa
```

**Reglas de negocio:**
- Los usuarios no pueden desuscribirse del canal de su carrera (suscripción obligatoria)
- `is_admin = True` permite al usuario crear, editar y eliminar publicaciones en ese canal

#### 5. **Posts** (Publicaciones)

Contenido compartido en canales.

```python
- post_id (PK)              # ID único
- channel_id (FK)           # Canal donde se publica
- user_id (FK)              # Autor
- title                     # Título
- tags                      # Etiquetas (string, posiblemente JSON)
- content                   # Contenido
- date                      # Fecha de publicación
```

#### 6. **Events** (Eventos)

Eventos académicos o de comunidad.

```python
- event_id (PK)             # ID único
- event_title               # Título
- event_description         # Descripción
- event_date                # Fecha del evento
- event_start_hour          # Hora de inicio
- event_final_hour          # Hora de fin
- notification_datetime     # Cuándo notificar
- all_day                   # True = evento todo el día
- user_id (FK)              # Creador
```

#### 7. **Courses** (Cursos)

Cursos o talleres ofrecidos.

```python
- course_id (PK)            # ID único
- course_title              # Título
- course_type               # Tipo (1=taller, 2=curso, etc.)
- location                  # Ubicación
- schedule                  # Horario (posiblemente JSON)
- course_start_date         # Fecha inicio
- course_final_date         # Fecha fin
- notification_datetime     # Notificaciones
- user_id (FK)              # Usuario inscrito
- professor_id (FK)         # Profesor
```

#### 8. **Professors** (Profesores)

Instructores de cursos.

```python
- professor_id (PK)         # ID único
- professor_name            # Nombre
- professor_lastname        # Apellido
```

**Relaciones:**
- Puede pertenecer a múltiples `Areas` a través de `ProfessorAreas`
- Puede tener múltiples `Courses` asociados

#### 9. **ProfessorAreas** (Relación Profesor-Área)

Tabla intermedia que permite la relación muchos a muchos entre profesores y áreas académicas. Un profesor puede dar clases en múltiples carreras.

```python
- id (PK)                   # ID único
- professor_id (FK)         # Profesor
- area_id (FK)              # Área académica
- UNIQUE(professor_id, area_id)  # Evita duplicados
```

**Relaciones:**
- Pertenece a un `Professor`
- Pertenece a un `Area`

#### 10. **Activities** (Actividades)

Actividades programadas por el usuario.

```python
- activity_id (PK)          # ID único
- activity_title            # Título
- location                  # Ubicación
- schedule                  # Horario (JSON serializado)
- activity_start_date       # Fecha de inicio
- activity_final_date       # Fecha final
- notification_datetime     # Notificaciones
- user_id (FK)              # Creador
```

---

## Autenticación

### Sistema de Autenticación Basado en Dominios

La plataforma valida que los usuarios pertenezcan al TEC mediante sus dominios de correo.

#### Dominios Permitidos

```python
_providers = {
    'tec.cr': TecAuthProvider,
    'estudiantec.cr': TecAuthProvider,
    'itcr.ac.cr': TecAuthProvider
}
```

#### Flujo de Autenticación

1. **Registro (Signup)**
   - Usuario envía: nombre, apellido, email, contraseña, carnet, género, fecha nacimiento, área
   - Sistema valida dominio de email
   - Sistema verifica que email y carnet no existan
   - Contraseña se hashea con bcrypt
   - Usuario se suscribe automáticamente a:
     - Canal principal del área
     - Canales específicos: DEVESA, Ciencias Naturales, Ciencias del Lenguaje

2. **Login**
   - Usuario envía: email y contraseña
   - Sistema valida dominio
   - Sistema busca usuario por email
   - Sistema verifica contraseña hasheada
   - Retorna datos del usuario

#### Hasheo de Contraseñas

```python
# Usando bcrypt con passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para crear
hashed_password = pwd_context.hash(plain_password)

# Para verificar
is_valid = pwd_context.verify(plain_password, hashed_password)
```

---

## Endpoints de la API

### 1. Users (Usuarios)

#### POST `/api/users/user_create`
**Crear nuevo usuario (Registro)**

Request:
```json
{
  "name": "Juan",
  "lastname": "Pérez",
  "mail": "juan.perez@tec.cr",
  "password": "securePassword123",
  "carnet_number": "2024001234",
  "gender": "M",
  "birth_date": "2000-05-15",
  "area_id": 5
}
```

Response (201):
```json
{
  "user_id": 1,
  "name": "Juan",
  "lastname": "Pérez",
  "mail": "juan.perez@tec.cr",
  "area_id": 5,
  "full_name": "Juan Pérez"
}
```

#### POST `/api/users/user_login`
**Iniciar sesión**

Request:
```json
{
  "mail": "juan.perez@tec.cr",
  "password": "securePassword123"
}
```

Response (200):
```json
{
  "user_id": 1,
  "name": "Juan",
  "lastname": "Pérez",
  "mail": "juan.perez@tec.cr",
  "full_name": "Juan Pérez"
}
```

#### GET `/api/users/next_activities?user_id=1`
**Obtener próximas actividades del usuario**

Response (200):
```json
[
  {
    "activity_id": 1,
    "activity_name": "Proyecto Final",
    "description": "Entregar proyecto",
    "due_date": "2026-02-15"
  }
]
```

#### PUT `/api/users/activate?user_id=1`
**Activar usuario**

Response (200):
```json
{
  "message": "Usuario activado",
  "user_id": 1,
  "is_active": true
}
```

### 2. Areas (Áreas Académicas)

#### GET `/api/areas/`
**Listar todas las áreas**

Response (200):
```json
[
  {
    "area_id": 1,
    "area_name": "DEVESA",
    "is_major": false
  },
  {
    "area_id": 5,
    "area_name": "Ing. En Computación San Carlos",
    "is_major": true
  }
]
```

#### GET `/api/areas/{area_id}`
**Obtener área específica**

Response (200):
```json
{
  "area_id": 5,
  "area_name": "Ing. En Computación San Carlos",
  "is_major": true
}
```

#### POST `/api/areas/create`
**Crear nueva área**

Request:
```json
{
  "area_name": "Nueva Escuela",
  "is_major": true
}
```

Response (201):
```json
{
  "area_id": 12,
  "area_name": "Nueva Escuela",
  "is_major": true
}
```

### 3. Channels (Canales)

#### GET `/api/channels/`
**Listar todos los canales**

Response (200):
```json
[
  {
    "channel_id": 1,
    "channel_name": "General Computación",
    "area_id": 5
  }
]
```

#### GET `/api/channels/area/{area_id}`
**Obtener canales de un área**

Response (200):
```json
[
  {
    "channel_id": 1,
    "channel_name": "General Computación",
    "area_id": 5
  }
]
```

#### POST `/api/channels/create`
**Crear nuevo canal**

Request:
```json
{
  "channel_name": "Proyectos",
  "area_id": 5
}
```

Response (201):
```json
{
  "channel_id": 2,
  "channel_name": "Proyectos",
  "area_id": 5
}
```

### 4. Subscriptions (Suscripciones)

#### POST `/api/subscriptions/`
**Suscribir usuario a canal**

Request:
```json
{
  "user_id": 1,
  "channel_id": 2,
  "is_admin": false,
  "is_favorite": false
}
```

Response (201):
```json
{
  "subscription_id": 1,
  "user_id": 1,
  "channel_id": 2,
  "is_admin": false,
  "is_favorite": false
}
```

#### GET `/api/subscriptions/user/{user_id}`
**Obtener suscripciones de un usuario**

Response (200):
```json
[
  {
    "subscription_id": 1,
    "user_id": 1,
    "channel_id": 1,
    "is_admin": false,
    "is_favorite": true
  }
]
```

#### PUT `/api/subscriptions/{subscription_id}/favorite`
**Marcar suscripción como favorita**

Response (200):
```json
{
  "subscription_id": 1,
  "is_favorite": true
}
```

#### DELETE `/api/subscriptions/{subscription_id}`
**Desuscribir usuario de canal**

Response (200):
```json
{
  "message": "Desuscrito exitosamente"
}
```

### 5. Posts (Publicaciones)

#### POST `/api/posts/create`
**Crear publicación**

Request:
```json
{
  "channel_id": 1,
  "user_id": 1,
  "title": "Actualizacion del proyecto",
  "tags": "proyecto,actualizacion",
  "content": "Se ha actualizado el código..."
}
```

Response (201):
```json
{
  "post_id": 1,
  "channel_id": 1,
  "user_id": 1,
  "title": "Actualizacion del proyecto",
  "tags": "proyecto,actualizacion",
  "content": "Se ha actualizado el código...",
  "date": "2026-01-31T10:30:00"
}
```

#### GET `/api/posts/channel/{channel_id}`
**Obtener posts de un canal**

Response (200):
```json
[
  {
    "post_id": 1,
    "channel_id": 1,
    "user_id": 1,
    "title": "Actualizacion del proyecto",
    "tags": "proyecto,actualizacion",
    "content": "Se ha actualizado el código...",
    "date": "2026-01-31T10:30:00"
  }
]
```

#### DELETE `/api/posts/{post_id}`
**Eliminar publicación**

Response (200):
```json
{
  "message": "Post eliminado"
}
```

### 6. Events (Eventos)

#### POST `/api/events/create`
**Crear evento**

Request:
```json
{
  "event_title": "Conferencia de Tecnología",
  "event_description": "Una conferencia sobre nuevas tecnologías",
  "event_date": "2026-02-15",
  "event_start_hour": "2026-02-15T14:00:00",
  "event_final_hour": "2026-02-15T16:00:00",
  "all_day": false,
  "user_id": 1,
  "notification_datetime": "2026-02-14T14:00:00"
}
```

Response (201):
```json
{
  "event_id": 1,
  "event_title": "Conferencia de Tecnología",
  "event_description": "Una conferencia sobre nuevas tecnologías",
  "event_date": "2026-02-15",
  "event_start_hour": "2026-02-15T14:00:00",
  "event_final_hour": "2026-02-15T16:00:00",
  "all_day": false,
  "user_id": 1,
  "notification_datetime": "2026-02-14T14:00:00"
}
```

#### GET `/api/events/user/{user_id}`
**Obtener eventos del usuario**

Response (200):
```json
[
  {
    "event_id": 1,
    "event_title": "Conferencia de Tecnología",
    ...
  }
]
```

### 7. Courses (Cursos)

#### POST `/api/courses/create`
**Crear curso**

Request:
```json
{
  "course_title": "Python Avanzado",
  "course_type": 1,
  "location": "Aula 101",
  "schedule": "Lunes y Miércoles 14:00-16:00",
  "course_start_date": "2026-02-01",
  "course_final_date": "2026-04-30",
  "user_id": 1,
  "professor_id": 1,
  "notification_datetime": "2026-02-01T13:00:00"
}
```

Response (201):
```json
{
  "course_id": 1,
  "course_title": "Python Avanzado",
  "course_type": 1,
  "location": "Aula 101",
  ...
}
```

#### GET `/api/courses/user/{user_id}`
**Obtener cursos del usuario**

Response (200):
```json
[
  {
    "course_id": 1,
    "course_title": "Python Avanzado",
    ...
  }
]
```

### 8. Professors (Profesores)

#### GET `/api/professors/?area_id={area_id}`
**Listar profesores (filtrado opcional por área)**

El parámetro `area_id` es opcional. Si se omite, retorna todos los profesores. Si se incluye, retorna solo los profesores asignados a esa área.

Response (200):
```json
[
  {
    "professor_id": 1,
    "professor_name": "Carlos",
    "professor_lastname": "Ramírez",
    "areas": [
      {
        "area_id": 5,
        "area_name": "Ing. En Computación San Carlos"
      }
    ]
  }
]
```

#### POST `/api/professors/create`
**Crear nuevo profesor (Admin)**

Request:
```json
{
  "professor_name": "Carlos",
  "professor_lastname": "Ramírez"
}
```

Response (201):
```json
{
  "msg": "SUCCESS",
  "professor_id": 1
}
```

#### POST `/api/professors/assign_area`
**Asignar profesor a un área (Admin)**

Request:
```json
{
  "professor_id": 1,
  "area_id": 5
}
```

Response (201):
```json
{
  "msg": "SUCCESS"
}
```

#### DELETE `/api/professors/remove_area?professor_id=1&area_id=5`
**Remover profesor de un área (Admin)**

Response (200):
```json
{
  "msg": "SUCCESS"
}
```

### 9. Posts - Endpoints Adicionales

#### PUT `/api/posts/update/{post_id}?user_id={user_id}`
**Editar publicación (requiere is_admin en el canal)**

Request:
```json
{
  "title": "Título actualizado",
  "content": "Contenido actualizado",
  "tags": "nuevos,tags"
}
```

#### DELETE `/api/posts/delete/{post_id}?user_id={user_id}`
**Eliminar publicación (requiere is_admin en el canal)**

---

## Flujos Principales

### Flujo 1: Registro e Incorporación de Usuario

```
1. Cliente envia POST /api/users/user_create
   ↓
2. Route valida dominio de email mediante AuthFactory
   ↓
3. Controller create_user:
   - Valida email único
   - Valida carnet único
   - Hashea contraseña
   - Crea usuario en BD
   - Busca canal principal del área
   - Suscribe usuario a canal principal
   - Busca 3 canales específicos (DEVESA, Ciencias Naturales, Ciencias Lenguaje)
   - Suscribe usuario a esos canales
   ↓
4. Retorna datos del usuario creado
```

### Flujo 2: Login de Usuario

```
1. Cliente envia POST /api/users/user_login
   ↓
2. Route valida dominio mediante AuthFactory
   ↓
3. Controller login:
   - Busca usuario por email
   - Verifica contraseña hasheada
   - Actualiza last_login
   - Retorna datos del usuario
   ↓
4. Cliente recibe token/datos para usar en futuras solicitudes
```

### Flujo 3: Crear y Ver Publicación en Canal

```
1. Usuario crea POST: POST /api/posts/create
   ↓
2. Controller:
   - Valida que usuario esté suscrito al canal
   - Crea publicación con timestamp
   - Guarda en BD
   ↓
3. Otros usuarios ven: GET /api/posts/channel/{channel_id}
   ↓
4. Se retornan posts en orden de fecha
```

### Flujo 4: Suscripción a Canal

```
1. Usuario ejecuta: POST /api/subscriptions/
   ↓
2. Controller:
   - Verifica que usuario y canal existan
   - Verifica que no esté ya suscrito
   - Crea subscription
   ↓
3. Usuario ahora puede ver posts del canal
```

---

## Patrones de Código

### 1. Inyección de Dependencias (Dependency Injection)

FastAPI usa inyección de dependencias para conectar rutas con controladores y BD:

```python
# En routes
@user_router.post("/user_create")
def create_user_route(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # db se inyecta automáticamente
    return provider.create_user(user, db)

# get_db es una dependencia que proporciona la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Validación con Pydantic Schemas

Los schemas definen la estructura de entrada/salida:

```python
# schemas/users_schemas.py
class UserBase(BaseModel):
    name: str
    lastname: str
    mail: EmailStr
    area_id: int
    carnet_number: str
    gender: str
    birth_date: date

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    full_name: str
```

### 3. ORM con SQLAlchemy

Los modelos representan tablas:

```python
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    
    # Relaciones
    area = relationship("Area", back_populates="users")
    subscriptions = relationship("Subscription", back_populates="user")
```

### 4. Factory Pattern para Autenticación

```python
# interfaces/auth_factory.py
class AuthFactory:
    _providers = {
        'tec.cr': TecAuthProvider,
        'estudiantec.cr': TecAuthProvider,
    }
    
    @staticmethod
    def get_auth_provider(email: str) -> AuthProvider:
        domain = email.split('@')[-1]
        provider_class = AuthFactory._providers.get(domain)
        if provider_class is None:
            raise ValueError(f"Domain '{domain}' not supported")
        return provider_class()
```

### 5. Separación de Responsabilidades

```
Route → Controller → Model → Database
  ↓         ↓          ↓
HTTP    Lógica    Queries
Input   Negocio   SQL
```

---

## Gestión de Errores

### Códigos HTTP Usados

| Código | Situación |
|--------|-----------|
| 200 | Éxito en GET/PUT/DELETE |
| 201 | Creación exitosa (POST) |
| 400 | Error en validación |
| 404 | Recurso no encontrado |
| 409 | Conflicto (email/carnet duplicado) |
| 500 | Error del servidor |

### Ejemplos de Errores

```python
# Email ya registrado
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Email already registered"
)

# Dominio no permitido
raise HTTPException(
    status_code=400,
    detail="Dominio de correo no permitido"
)

# Usuario no encontrado
raise HTTPException(
    status_code=404,
    detail="User not found"
)
```

---

## Desarrollo y Despliegue

### Ejecución Local

```bash
# Modo desarrollo con auto-reload
python run_server.py

# O directamente
python -m uvicorn app:app --reload --port 8000
```

La API estará disponible en: `http://localhost:8000`

### Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Testing

```bash
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

### Configuración CORS

En `app.py` se permite CORS (actualmente todos los orígenes):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, usar lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Variables Importantes para Producción

```python
# En database/db_config.py
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

# En app.py
allow_origins=["https://mi-dominio.com", "https://www.mi-dominio.com"]
```

### Docker (Opcional)

Para contenedores:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0"]
```

---

## Validaciones de Datos (Pydantic Schemas)

Las siguientes validaciones se aplican automáticamente al recibir datos en los endpoints. Si alguna falla, se retorna un error 422 con el mensaje correspondiente.

### Eventos (`EventCreate`)
| Campo | Validación |
|-------|-----------|
| `event_title` | No puede estar vacío (se aplica trim) |
| `event_description` | No puede estar vacío (se aplica trim) |
| `event_date` | No puede ser una fecha en el pasado |
| `event_start_hour` / `event_final_hour` | La hora de inicio debe ser antes de la hora de fin |

### Cursos (`CourseCreate`)
| Campo | Validación |
|-------|-----------|
| `course_title` | No puede estar vacío (se aplica trim) |
| `location` | No puede estar vacío (se aplica trim) |
| `schedule` | No puede estar vacío; cada entrada debe tener `date` (día válido en inglés: monday-sunday) y `start_time` (formato HH:MM) |
| `course_start_date` / `course_final_date` | La fecha de inicio debe ser antes de la fecha final |

### Actividades (`ActivityCreate`)
| Campo | Validación |
|-------|-----------|
| `activity_title` | No puede estar vacío (se aplica trim) |
| `location` | No puede estar vacío (se aplica trim) |
| `schedule` | No puede estar vacío; cada entrada debe tener `date` (día válido en inglés: monday-sunday) y `start_time` (formato HH:MM) |
| `activity_start_date` / `activity_final_date` | La fecha de inicio debe ser antes de la fecha final |

### Profesores (`ProfessorBase`)
| Campo | Validación |
|-------|-----------|
| `professor_name` | No puede estar vacío (se aplica trim) |
| `professor_lastname` | No puede estar vacío (se aplica trim) |

---

## Consideraciones de Seguridad

1. **Contraseñas**: Se hashean con bcrypt, nunca se almacenan en texto plano
2. **Validación de Email**: Solo dominios TEC permitidos
3. **Datos Únicos**: Email y carnet_number no pueden duplicarse
4. **CORS**: En producción, usar lista blanca específica
5. **Validación de Input**: Pydantic valida todos los campos
6. **Inyección SQL**: SQLAlchemy previene automaticamente

---

## Troubleshooting Común

### Error: "pg_config executable not found"
**Solución**: Instalar PostgreSQL client o usar psycopg2-binary precompilado

### Error: "Email already registered"
**Solución**: El email ya existe. Usar otro email o resetear BD

### Error: "Dominio de correo no permitido"
**Solución**: Usar email con dominio TEC (tec.cr, estudiantec.cr, itcr.ac.cr)

### Error: "Connection refused"
**Solución**: Verificar que PostgreSQL esté ejecutando en localhost:5432

---

## Próximos Pasos para Mantenimiento

1. **Agregar autenticación token**: Implementar JWT para sesiones
2. **Agregar roles**: Diferenciación entre admin, profesor, estudiante
3. **Validación avanzada**: Validar carnet según formato TEC
4. **Notificaciones**: Sistema de notificaciones en tiempo real
5. **Tests adicionales**: Mayor cobertura de tests
6. **Rate limiting**: Limitar solicitudes por IP/usuario
7. **Logging**: Sistema de logs detallado
8. **Caché**: Redis para mejorar performance

---

**Última actualización**: 28 de Febrero, 2026
**Versión del Proyecto**: 1.1
**Autor**: Equipo de Desarrollo Asistec

### Historial de Cambios

#### v1.1 (28/02/2026)
- **Nueva tabla `professor_areas`**: Relación muchos a muchos entre profesores y áreas académicas, permitiendo que un profesor esté asociado a múltiples carreras
- **Nuevos endpoints de profesores**: Filtrado por área, asignación y remoción de áreas
- **Validaciones de datos mejoradas**: Validaciones en schemas de eventos, cursos, actividades y profesores (campos no vacíos, fechas no en el pasado, formatos de horario, etc.)
- **Administración de canales**: Endpoints para crear, editar y eliminar publicaciones (requiere `is_admin` en la suscripción del canal)
- **Corrección de modelo**: `is_favorite` renombrado a `is_subscribed` en suscripciones
- **Protección de suscripción**: Los usuarios no pueden desuscribirse del canal de su carrera
- **Filtro de noticias recientes**: El endpoint de noticias solo muestra publicaciones de los últimos 3 días de canales suscritos

#### v1.0 (31/01/2026)
- Versión inicial del proyecto
