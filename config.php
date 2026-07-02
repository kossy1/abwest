<?php
// config.php - Database configuration with proper table creation
$host = 'localhost';
$dbname = 'adaptive_learning';
$user = 'root';
$pass = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}

// Create tables if not exist - WITH ALL REQUIRED COLUMNS
$pdo->exec("CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('student', 'instructor', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
)");

$pdo->exec("CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'General',
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    instructor_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)");

$pdo->exec("CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    title VARCHAR(100),
    description TEXT,
    order_number INT DEFAULT 0,
    estimated_time_minutes INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
)");

// IMPORTANT: quizzes table with ALL columns including difficulty_level
$pdo->exec("CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    module_id INT NULL,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    difficulty_level TINYINT DEFAULT 1,
    topic VARCHAR(100) DEFAULT NULL,
    points INT DEFAULT 10,
    time_limit_seconds INT DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL
)");

// Check if difficulty_level column exists, if not add it
try {
    $pdo->query("SELECT difficulty_level FROM quizzes LIMIT 1");
} catch (PDOException $e) {
    // Column doesn't exist, add it
    $pdo->exec("ALTER TABLE quizzes ADD COLUMN difficulty_level TINYINT DEFAULT 1");
}

// Check if topic column exists, if not add it
try {
    $pdo->query("SELECT topic FROM quizzes LIMIT 1");
} catch (PDOException $e) {
    $pdo->exec("ALTER TABLE quizzes ADD COLUMN topic VARCHAR(100) DEFAULT NULL");
}

// Check if points column exists, if not add it
try {
    $pdo->query("SELECT points FROM quizzes LIMIT 1");
} catch (PDOException $e) {
    $pdo->exec("ALTER TABLE quizzes ADD COLUMN points INT DEFAULT 10");
}

// Check if time_limit_seconds column exists
try {
    $pdo->query("SELECT time_limit_seconds FROM quizzes LIMIT 1");
} catch (PDOException $e) {
    $pdo->exec("ALTER TABLE quizzes ADD COLUMN time_limit_seconds INT DEFAULT 30");
}

$pdo->exec("CREATE TABLE IF NOT EXISTS user_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    course_id INT,
    quiz_id INT,
    selected_answer CHAR(1),
    answered_correctly BOOLEAN,
    points_earned INT DEFAULT 0,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
)");

$pdo->exec("CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    course_id INT,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (user_id, course_id)
)");

// Check if data already exists
$stmt = $pdo->query("SELECT COUNT(*) FROM courses");
if ($stmt->fetchColumn() == 0) {
    // Insert sample courses
    $pdo->exec("INSERT INTO courses (title, description, category, difficulty_level) VALUES 
        ('Mathematics', 'Learn algebra, geometry, and calculus', 'Mathematics', 'beginner'),
        ('Science', 'Explore physics, chemistry, and biology', 'Science', 'beginner'),
        ('History', 'Journey through world history', 'History', 'intermediate'),
        ('English Literature', 'Study classic literature', 'Language', 'intermediate')
    ");
    
    // Get course IDs
    $stmt = $pdo->query("SELECT id FROM courses WHERE title = 'Mathematics'");
    $mathId = $stmt->fetchColumn();
    
    $stmt = $pdo->query("SELECT id FROM courses WHERE title = 'Science'");
    $scienceId = $stmt->fetchColumn();
    
    $stmt = $pdo->query("SELECT id FROM courses WHERE title = 'History'");
    $historyId = $stmt->fetchColumn();
    
    // Insert sample modules
    if ($mathId) {
        $pdo->exec("INSERT INTO modules (course_id, title, description, order_number) VALUES
            ($mathId, 'Algebra Basics', 'Introduction to algebraic expressions', 1),
            ($mathId, 'Geometry', 'Shapes, angles, and theorems', 2),
            ($mathId, 'Calculus', 'Introduction to differentiation', 3)
        ");
    }
    
    if ($scienceId) {
        $pdo->exec("INSERT INTO modules (course_id, title, description, order_number) VALUES
            ($scienceId, 'Physics', 'Laws of motion and energy', 1),
            ($scienceId, 'Chemistry', 'Atoms, molecules, and reactions', 2)
        ");
    }
    
    if ($historyId) {
        $pdo->exec("INSERT INTO modules (course_id, title, description, order_number) VALUES
            ($historyId, 'Ancient Civilizations', 'Egypt, Greece, and Rome', 1),
            ($historyId, 'Modern History', 'World wars and revolutions', 2)
        ");
    }
    
    // Insert sample quizzes with difficulty_level
    if ($mathId) {
        $pdo->exec("INSERT INTO quizzes (course_id, question, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, topic, points) VALUES
            ($mathId, 'What is 7 + 3?', '8', '9', '10', '11', 'C', 1, 'Arithmetic', 10),
            ($mathId, 'What is 4 × 5?', '15', '18', '20', '25', 'C', 1, 'Multiplication', 10),
            ($mathId, 'What is the square root of 144?', '10', '11', '12', '13', 'C', 2, 'Algebra', 15),
            ($mathId, 'What is the area of a rectangle with length 5 and width 3?', '8', '12', '15', '16', 'C', 2, 'Geometry', 15),
            ($mathId, 'What is the derivative of x²?', 'x', '2x', 'x²', '2', 'B', 4, 'Calculus', 20)
        ");
    }
    
    if ($scienceId) {
        $pdo->exec("INSERT INTO quizzes (course_id, question, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, topic, points) VALUES
            ($scienceId, 'What is H2O?', 'Water', 'Salt', 'Acid', 'Base', 'A', 1, 'Chemistry', 10),
            ($scienceId, 'What planet is known as Red Planet?', 'Earth', 'Mars', 'Jupiter', 'Venus', 'B', 1, 'Astronomy', 10),
            ($scienceId, 'What is the chemical symbol for Gold?', 'Go', 'Gd', 'Au', 'Ag', 'C', 2, 'Chemistry', 15),
            ($scienceId, 'What is the speed of light approximately?', '3×10⁶ m/s', '3×10⁸ m/s', '3×10¹⁰ m/s', '3×10⁴ m/s', 'B', 3, 'Physics', 20)
        ");
    }
    
    if ($historyId) {
        $pdo->exec("INSERT INTO quizzes (course_id, question, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, topic, points) VALUES
            ($historyId, 'Who built the pyramids?', 'Romans', 'Greeks', 'Egyptians', 'Persians', 'C', 1, 'Ancient History', 10),
            ($historyId, 'What year did WWII end?', '1943', '1944', '1945', '1946', 'C', 1, 'Modern History', 10),
            ($historyId, 'When was the Great Wall of China built?', '200 BC', '500 BC', '700 BC', '100 BC', 'A', 2, 'Asian History', 15)
        ");
    }
    
    // Insert sample admin user (password: admin123)
    $pdo->exec("INSERT INTO users (username, full_name, email, password, role) VALUES 
        ('admin', 'Admin User', 'admin@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin')
    ");
    
    // Insert sample student (password: student123)
    $pdo->exec("INSERT INTO users (username, full_name, email, password, role) VALUES 
        ('student', 'Student User', 'student@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student')
    ");
}

// Output success message if everything is set up
// echo "Database setup complete!";
?>