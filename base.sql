DROP DATABASE IF EXISTS metas_app;
CREATE DATABASE metas_app;
USE metas_app;

-- ======================
-- TABLA USUARIOS
-- ======================
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ======================
-- TABLA CATEGORIAS
-- ======================
CREATE TABLE categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);

-- ======================
-- TABLA METAS
-- ======================
CREATE TABLE metas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  categoria_id INT,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  progreso INT DEFAULT 0 CHECK (progreso >= 0 AND progreso <= 100),
  estado ENUM('pendiente','en progreso','completado') DEFAULT 'pendiente',
  fecha_inicio DATE,
  fecha_limite DATE,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
);

-- ======================
-- DATOS DE PRUEBA
-- ======================
INSERT INTO usuarios (nombre, email, password)
VALUES ('Saul', 'saul@email.com', '123456');

INSERT INTO categorias (nombre) VALUES
('Salud'),('Estudio'),('Finanzas');

INSERT INTO metas (usuario_id, categoria_id, titulo, descripcion, progreso, estado, fecha_inicio, fecha_limite)
VALUES
(1,1,'Ir al gym','3 veces por semana',30,'en progreso','2026-04-01','2026-06-01');