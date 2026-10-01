-- ============================================
-- AI Task Assistant Database
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS ai_tasks;

-- Select database
USE ai_tasks;

-- ============================================
-- Tasks table
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_text VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Test data
-- ============================================

INSERT INTO tasks (task_text)
VALUES
('Finish database assignment'),
('Study React'),
('Apply for software internship');

-- ============================================
-- Check the data
-- ============================================

SELECT * FROM tasks;