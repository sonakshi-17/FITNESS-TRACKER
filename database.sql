CREATE DATABASE IF NOT EXISTS fitness_trac;
USE fitness_trac;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  age INT NOT NULL,
  weight DECIMAL(5,2) NOT NULL,
  sex ENUM('male', 'female') NOT NULL,
  goal ENUM('lose_weight', 'maintain', 'gain_muscle') NOT NULL DEFAULT 'maintain',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intake_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  log_date DATE NOT NULL DEFAULT (CURRENT_DATE),
  calories INT DEFAULT 0,
  water DECIMAL(4,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_day (user_id, log_date),
  CONSTRAINT fk_intake_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
