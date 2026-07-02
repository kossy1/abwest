<?php
// functions.php - Core functions with correct column names

function loginUser($email, $password) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($user && password_verify($password, $user['password'])) {
        return $user;
    }
    return false;
}

function registerUser($name, $email, $password) {
    global $pdo;
    $hashed = password_hash($password, PASSWORD_DEFAULT);
    try {
        $stmt = $pdo->prepare("INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, 'student')");
        return $stmt->execute([$name, $email, $hashed]);
    } catch (PDOException $e) {
        return false;
    }
}

function getCourses() {
    global $pdo;
    $stmt = $pdo->query("SELECT * FROM courses ORDER BY title");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getCourseById($courseId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT * FROM courses WHERE id = ?");
    $stmt->execute([$courseId]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

function getQuizzesForCourse($courseId, $userId = null) {
    global $pdo;
    if ($userId) {
        $stmt = $pdo->prepare("SELECT q.* FROM quizzes q WHERE q.course_id = ? AND q.id NOT IN 
            (SELECT quiz_id FROM user_progress WHERE user_id = ? AND answered_correctly = 1 AND course_id = ?)
            ORDER BY q.difficulty_level ASC LIMIT 5");
        $stmt->execute([$courseId, $userId, $courseId]);
    } else {
        $stmt = $pdo->prepare("SELECT * FROM quizzes WHERE course_id = ? ORDER BY difficulty_level ASC LIMIT 5");
        $stmt->execute([$courseId]);
    }
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getAllQuizzes() {
    global $pdo;
    $stmt = $pdo->query("SELECT q.*, c.title as course_title FROM quizzes q LEFT JOIN courses c ON q.course_id = c.id ORDER BY q.id DESC");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function recordProgress($userId, $courseId, $quizId, $correct) {
    global $pdo;
    $stmt = $pdo->prepare("INSERT INTO user_progress (user_id, course_id, quiz_id, answered_correctly) VALUES (?, ?, ?, ?)");
    return $stmt->execute([$userId, $courseId, $quizId, $correct]);
}

function getProgress($userId, $courseId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT COUNT(*) as total, SUM(answered_correctly) as correct FROM user_progress WHERE user_id = ? AND course_id = ?");
    $stmt->execute([$userId, $courseId]);
    $res = $stmt->fetch(PDO::FETCH_ASSOC);
    return ['total' => $res['total'] ?? 0, 'correct' => $res['correct'] ?? 0];
}

function getCourseName($courseId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT title FROM courses WHERE id = ?");
    $stmt->execute([$courseId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return $row ? $row['title'] : 'Unknown';
}

function getUserName($userId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT full_name FROM users WHERE id = ?");
    $stmt->execute([$userId]);
    return $stmt->fetchColumn();
}

function getModuleName($moduleId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT title FROM modules WHERE id = ?");
    $stmt->execute([$moduleId]);
    return $stmt->fetchColumn();
}

function getModulesByCourse($courseId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT * FROM modules WHERE course_id = ? ORDER BY order_number");
    $stmt->execute([$courseId]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getUserProgressSummary($userId) {
    global $pdo;
    $stmt = $pdo->prepare("
        SELECT 
            c.id as course_id,
            c.title as course_title,
            COUNT(DISTINCT q.id) as total_quizzes,
            COUNT(DISTINCT CASE WHEN up.answered_correctly = 1 THEN up.quiz_id END) as correct_answers,
            ROUND(COUNT(DISTINCT CASE WHEN up.answered_correctly = 1 THEN up.quiz_id END) / NULLIF(COUNT(DISTINCT q.id), 0) * 100, 2) as progress_percentage
        FROM courses c
        LEFT JOIN quizzes q ON c.id = q.course_id
        LEFT JOIN user_progress up ON q.id = up.quiz_id AND up.user_id = ?
        GROUP BY c.id
    ");
    $stmt->execute([$userId]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function isAdmin($userId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT role FROM users WHERE id = ?");
    $stmt->execute([$userId]);
    $role = $stmt->fetchColumn();
    return $role === 'admin';
}

function getQuestionsByCourse($courseId) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT * FROM quizzes WHERE course_id = ? ORDER BY difficulty_level");
    $stmt->execute([$courseId]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getTestHistory($userId = null, $courseId = null) {
    global $pdo;
    $sql = "SELECT up.*, u.full_name, u.email, q.question, q.correct_answer, c.title as course_title 
            FROM user_progress up
            JOIN users u ON up.user_id = u.id
            JOIN quizzes q ON up.quiz_id = q.id
            JOIN courses c ON up.course_id = c.id
            WHERE 1=1";
    $params = [];
    if ($userId) {
        $sql .= " AND up.user_id = ?";
        $params[] = $userId;
    }
    if ($courseId) {
        $sql .= " AND up.course_id = ?";
        $params[] = $courseId;
    }
    $sql .= " ORDER BY up.attempted_at DESC LIMIT 100";
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getAdminStats() {
    global $pdo;
    $stats = [];
    $stats['total_users'] = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
    $stats['total_courses'] = $pdo->query("SELECT COUNT(*) FROM courses")->fetchColumn();
    $stats['total_quizzes'] = $pdo->query("SELECT COUNT(*) FROM quizzes")->fetchColumn();
    $stats['total_attempts'] = $pdo->query("SELECT COUNT(*) FROM user_progress")->fetchColumn();
    $stats['active_today'] = $pdo->query("SELECT COUNT(DISTINCT user_id) FROM user_progress WHERE DATE(attempted_at) = CURDATE()")->fetchColumn();
    return $stats;
}

function bulkImportQuestions($courseId, $questions) {
    global $pdo;
    $count = 0;
    foreach ($questions as $q) {
        $stmt = $pdo->prepare("INSERT INTO quizzes (course_id, question, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, topic, points) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
        if ($stmt->execute([
            $courseId,
            $q['question'],
            $q['option_a'],
            $q['option_b'],
            $q['option_c'],
            $q['option_d'],
            $q['correct_answer'],
            $q['difficulty'] ?? 1,
            $q['topic'] ?? '',
            $q['points'] ?? 10
        ])) {
            $count++;
        }
    }
    return $count;
}

function getDifficultQuestions($userId, $courseId, $limit = 5) {
    global $pdo;
    $stmt = $pdo->prepare("
        SELECT q.* FROM quizzes q
        LEFT JOIN user_progress up ON q.id = up.quiz_id AND up.user_id = ?
        WHERE q.course_id = ? 
        AND (up.id IS NULL OR up.answered_correctly = 0)
        ORDER BY q.difficulty_level DESC
        LIMIT ?
    ");
    $stmt->execute([$userId, $courseId, $limit]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function getRecommendedQuestions($userId, $courseId, $limit = 5) {
    global $pdo;
    $stmt = $pdo->prepare("
        SELECT q.* FROM quizzes q
        LEFT JOIN user_progress up ON q.id = up.quiz_id AND up.user_id = ?
        WHERE q.course_id = ? AND up.id IS NULL
        ORDER BY q.difficulty_level = 3 DESC, q.difficulty_level ASC
        LIMIT ?
    ");
    $stmt->execute([$userId, $courseId, $limit]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Fix function to handle course_id properly
function getCourseIdByName($courseName) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT id FROM courses WHERE title = ?");
    $stmt->execute([$courseName]);
    return $stmt->fetchColumn();
}
?>