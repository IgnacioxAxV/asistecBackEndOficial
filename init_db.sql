-- =============================================================
--  AsisTEC — Script de inicialización de base de datos
--  PostgreSQL 14+
--
--  Uso:
--    psql -U postgres -c "CREATE DATABASE asistec;"
--    psql -U postgres -d asistec -f init_db.sql
--
--  Incluye:
--    1. Creación de todas las tablas
--    2. Datos semilla (áreas, canal AsisTEC, usuario admin)
--
--  Credenciales admin por defecto:
--    Email   : admin@estudiantec.cr
--    Password: Admin#1
-- =============================================================


-- -------------------------------------------------------------
--  TABLAS
-- -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS areas (
    area_id   VARCHAR(36)  PRIMARY KEY,
    area_name VARCHAR      NOT NULL UNIQUE,
    is_major  BOOLEAN      DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS channels (
    channel_id   VARCHAR(36) PRIMARY KEY,
    channel_name VARCHAR     NOT NULL UNIQUE,
    area_id      VARCHAR(36) REFERENCES areas(area_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id        VARCHAR(36)  PRIMARY KEY,
    name           VARCHAR      NOT NULL,
    lastname       VARCHAR      NOT NULL,
    mail           VARCHAR      NOT NULL UNIQUE,
    password       VARCHAR      NOT NULL,
    carnet_number  VARCHAR      NOT NULL,
    gender         VARCHAR      NOT NULL,
    birth_date     DATE         NOT NULL,
    area_id        VARCHAR(36)  REFERENCES areas(area_id),
    is_active      BOOLEAN      DEFAULT FALSE,
    last_login     TIMESTAMP    DEFAULT NOW(),
    user_type      VARCHAR      DEFAULT '1',
    profile_image  TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) REFERENCES users(user_id),
    channel_id      VARCHAR(36) REFERENCES channels(channel_id),
    is_admin        BOOLEAN     DEFAULT FALSE,
    is_subscribed   BOOLEAN     DEFAULT FALSE,
    CONSTRAINT uq_subscription_user_channel UNIQUE (user_id, channel_id)
);

CREATE TABLE IF NOT EXISTS posts (
    post_id    VARCHAR(36) PRIMARY KEY,
    channel_id VARCHAR(36) REFERENCES channels(channel_id),
    user_id    VARCHAR(36) REFERENCES users(user_id),
    title      VARCHAR     NOT NULL,
    tags       VARCHAR     NOT NULL,
    content    VARCHAR     NOT NULL,
    date       TIMESTAMP   DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    event_id           VARCHAR(36) PRIMARY KEY,
    event_title        VARCHAR     NOT NULL,
    event_description  VARCHAR     NOT NULL,
    event_date         DATE        NOT NULL,
    event_start_hour   TIMESTAMP,
    event_final_hour   TIMESTAMP,
    notification_datetime VARCHAR,
    all_day            BOOLEAN     DEFAULT FALSE,
    user_id            VARCHAR(36) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS professors (
    professor_id       VARCHAR(36) PRIMARY KEY,
    professor_name     VARCHAR     NOT NULL,
    professor_lastname VARCHAR     NOT NULL
);

CREATE TABLE IF NOT EXISTS professor_areas (
    id           VARCHAR(36) PRIMARY KEY,
    professor_id VARCHAR(36) NOT NULL REFERENCES professors(professor_id),
    area_id      VARCHAR(36) NOT NULL REFERENCES areas(area_id),
    CONSTRAINT uq_professor_area UNIQUE (professor_id, area_id)
);

CREATE TABLE IF NOT EXISTS courses (
    course_id             VARCHAR(36) PRIMARY KEY,
    course_title          VARCHAR     NOT NULL,
    course_type           INTEGER     NOT NULL,
    location              VARCHAR     NOT NULL,
    schedule              VARCHAR,
    course_start_date     TIMESTAMP   NOT NULL,
    course_final_date     TIMESTAMP   NOT NULL,
    notification_datetime VARCHAR,
    user_id               VARCHAR(36) REFERENCES users(user_id),
    professor_name        VARCHAR     NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
    activity_id           VARCHAR(36) PRIMARY KEY,
    activity_title        VARCHAR     NOT NULL,
    location              VARCHAR     NOT NULL,
    schedule              VARCHAR,
    activity_start_date   DATE        NOT NULL,
    activity_final_date   DATE        NOT NULL,
    notification_datetime VARCHAR,
    user_id               VARCHAR(36) REFERENCES users(user_id)
);


-- -------------------------------------------------------------
--  SEED — Áreas iniciales
-- -------------------------------------------------------------

INSERT INTO areas (area_id, area_name, is_major) VALUES
    (gen_random_uuid()::varchar, 'DEVESA',                                                  FALSE),
    (gen_random_uuid()::varchar, 'Escuela Ciencias Naturales y Exactas San Carlos',         FALSE),
    (gen_random_uuid()::varchar, 'Escuela de Ciencias del Lenguaje San Carlos',             FALSE),
    (gen_random_uuid()::varchar, 'Dirección de Campus Tecnológico Local San Carlos',        FALSE),
    (gen_random_uuid()::varchar, 'AsisTEC',                                                 FALSE),
    (gen_random_uuid()::varchar, 'Ing. En Computación San Carlos',                          TRUE),
    (gen_random_uuid()::varchar, 'Ing. Electrónica San Carlos',                             TRUE),
    (gen_random_uuid()::varchar, 'Ing. Producción Industrial San Carlos',                   TRUE),
    (gen_random_uuid()::varchar, 'Ing. Agronomía San Carlos',                               TRUE),
    (gen_random_uuid()::varchar, 'Administración de Empresas San Carlos',                   TRUE),
    (gen_random_uuid()::varchar, 'Gestión del Turismo Rural Sostenible San Carlos',         TRUE),
    (gen_random_uuid()::varchar, 'Gestión en Sostenibilidad Turística Sostenible San Carlos', TRUE)
ON CONFLICT (area_name) DO NOTHING;


-- -------------------------------------------------------------
--  SEED — Canal del sistema AsisTEC
-- -------------------------------------------------------------

INSERT INTO channels (channel_id, channel_name, area_id)
SELECT
    gen_random_uuid()::varchar,
    'Canal AsisTEC',
    area_id
FROM areas
WHERE area_name = 'AsisTEC'
ON CONFLICT (channel_name) DO NOTHING;


-- -------------------------------------------------------------
--  SEED — Usuario administrador
--  Password hash de "Admin#1" con bcrypt (cost 12)
-- -------------------------------------------------------------

INSERT INTO users (
    user_id, name, lastname, mail, password,
    carnet_number, gender, birth_date, area_id, is_active, user_type
)
SELECT
    gen_random_uuid()::varchar,
    'Admin', 'Asistec',
    'admin@estudiantec.cr',
    '$2b$12$pHMoJVe/bfkLyac.6FVwROOiHpTl7kj3.v0lXsHnYZFOv2XD7tHLy',
    '20242417', 'M', '1990-01-01',
    area_id, TRUE, '2'
FROM areas
WHERE area_name = 'DEVESA'
ON CONFLICT (mail) DO NOTHING;


-- -------------------------------------------------------------
--  SEED — Suscripción admin → Canal AsisTEC (como administrador)
-- -------------------------------------------------------------

INSERT INTO subscriptions (subscription_id, user_id, channel_id, is_admin, is_subscribed)
SELECT
    gen_random_uuid()::varchar,
    u.user_id,
    c.channel_id,
    TRUE,
    TRUE
FROM users u, channels c
WHERE u.mail = 'admin@estudiantec.cr'
  AND c.channel_name = 'Canal AsisTEC'
ON CONFLICT (user_id, channel_id) DO NOTHING;


-- -------------------------------------------------------------
--  FIN
-- -------------------------------------------------------------
