<?php
// admin_dashboard.php - Admin Dashboard with Question Management & Test History
session_start();
require_once 'config.php';
require_once 'functions.php';

// Check if user is admin
if (!isset($_SESSION['user_id']) || $_SESSION['user_role'] !== 'admin') {
    header('Location: index.php');
    exit;
}

$userId = $_SESSION['user_id'];
$userName = $_SESSION['user_name'];

// Handle question upload
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['add_question'])) {
        $course_id = $_POST['course_id'];
        $module_id = $_POST['module_id'] ?: null;
        $question = $_POST['question'];
        $option_a = $_POST['option_a'];
        $option_b = $_POST['option_b'];
        $option_c = $_POST['option_c'];
        $option_d = $_POST['option_d'];
        $correct_answer = $_POST['correct_answer'];
        $difficulty = $_POST['difficulty'];
        $topic = $_POST['topic'];
        $points = $_POST['points'];
        $time_limit = $_POST['time_limit'];
        
        $stmt = $pdo->prepare("INSERT INTO quizzes (course_id, module_id, question, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, topic, points, time_limit_seconds) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
        if ($stmt->execute([$course_id, $module_id, $question, $option_a, $option_b, $option_c, $option_d, $correct_answer, $difficulty, $topic, $points, $time_limit])) {
            $success = "Question added successfully!";
        } else {
            $error = "Failed to add question.";
        }
    }
    
    if (isset($_POST['delete_question'])) {
        $quiz_id = $_POST['quiz_id'];
        $stmt = $pdo->prepare("DELETE FROM quizzes WHERE id = ?");
        if ($stmt->execute([$quiz_id])) {
            $success = "Question deleted successfully!";
        } else {
            $error = "Failed to delete question.";
        }
    }
    
    if (isset($_POST['update_question'])) {
        $quiz_id = $_POST['quiz_id'];
        $question = $_POST['question'];
        $option_a = $_POST['option_a'];
        $option_b = $_POST['option_b'];
        $option_c = $_POST['option_c'];
        $option_d = $_POST['option_d'];
        $correct_answer = $_POST['correct_answer'];
        $difficulty = $_POST['difficulty'];
        $topic = $_POST['topic'];
        $points = $_POST['points'];
        
        $stmt = $pdo->prepare("UPDATE quizzes SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?, difficulty_level = ?, topic = ?, points = ? WHERE id = ?");
        if ($stmt->execute([$question, $option_a, $option_b, $option_c, $option_d, $correct_answer, $difficulty, $topic, $points, $quiz_id])) {
            $success = "Question updated successfully!";
        } else {
            $error = "Failed to update question.";
        }
    }
}

// Get statistics
$stats = [];
$stats['total_users'] = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
$stats['total_courses'] = $pdo->query("SELECT COUNT(*) FROM courses")->fetchColumn();
$stats['total_quizzes'] = $pdo->query("SELECT COUNT(*) FROM quizzes")->fetchColumn();
$stats['total_attempts'] = $pdo->query("SELECT COUNT(*) FROM user_progress")->fetchColumn();

// Get courses for dropdown
$courses = $pdo->query("SELECT id, title FROM courses ORDER BY title")->fetchAll(PDO::FETCH_ASSOC);

// Get modules for dropdown
$modules = $pdo->query("SELECT id, title, course_id FROM modules ORDER BY title")->fetchAll(PDO::FETCH_ASSOC);

// Get all questions with course and module info
$questions = $pdo->query("
    SELECT q.*, c.title as course_title, m.title as module_title 
    FROM quizzes q
    LEFT JOIN courses c ON q.course_id = c.id
    LEFT JOIN modules m ON q.module_id = m.id
    ORDER BY q.id DESC
")->fetchAll(PDO::FETCH_ASSOC);

// Get recent test history
$recentHistory = $pdo->query("
    SELECT up.*, u.full_name, u.email, q.question, c.title as course_title, q.correct_answer
    FROM user_progress up
    JOIN users u ON up.user_id = u.id
    JOIN quizzes q ON up.quiz_id = q.id
    JOIN courses c ON up.course_id = c.id
    ORDER BY up.attempted_at DESC
    LIMIT 50
")->fetchAll(PDO::FETCH_ASSOC);

// Get user performance summary
$userPerformance = $pdo->query("
    SELECT 
        u.id,
        u.full_name,
        u.email,
        COUNT(DISTINCT up.course_id) as courses_attempted,
        COUNT(up.id) as total_attempts,
        SUM(CASE WHEN up.answered_correctly = 1 THEN 1 ELSE 0 END) as correct_answers,
        ROUND(SUM(CASE WHEN up.answered_correctly = 1 THEN 1 ELSE 0 END) / COUNT(up.id) * 100, 2) as success_rate
    FROM users u
    LEFT JOIN user_progress up ON u.id = up.user_id
    WHERE u.role = 'student'
    GROUP BY u.id
    ORDER BY success_rate DESC
")->fetchAll(PDO::FETCH_ASSOC);

// Get course-wise statistics
$courseStats = $pdo->query("
    SELECT 
        c.id,
        c.title,
        COUNT(DISTINCT q.id) as total_questions,
        COUNT(DISTINCT up.user_id) as unique_students,
        COUNT(up.id) as total_attempts,
        ROUND(AVG(CASE WHEN up.answered_correctly = 1 THEN 1 ELSE 0 END) * 100, 2) as avg_success_rate
    FROM courses c
    LEFT JOIN quizzes q ON c.id = q.course_id
    LEFT JOIN user_progress up ON c.id = up.course_id
    GROUP BY c.id
")->fetchAll(PDO::FETCH_ASSOC);

// Get question difficulty distribution
$difficultyDistribution = $pdo->query("
    SELECT difficulty_level, COUNT(*) as count 
    FROM quizzes 
    GROUP BY difficulty_level 
    ORDER BY difficulty_level
")->fetchAll(PDO::FETCH_ASSOC);

// Get daily activity for last 7 days
$dailyActivity = $pdo->query("
    SELECT DATE(attempted_at) as date, COUNT(*) as attempts 
    FROM user_progress 
    WHERE attempted_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    GROUP BY DATE(attempted_at)
    ORDER BY date
")->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Adaptive Learning Platform</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .admin-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border-left: 4px solid #3b82f6;
        }
        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: #0f172a;
        }
        .stat-card .label {
            color: #64748b;
            font-size: 0.9rem;
        }
        .tab-container {
            margin-top: 30px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab-btn {
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #64748b;
            border-bottom: 3px solid transparent;
            transition: 0.2s;
        }
        .tab-btn.active {
            color: #3b82f6;
            border-bottom-color: #3b82f6;
        }
        .tab-btn:hover {
            color: #0f172a;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .table-wrapper {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th {
            background: #f1f5f9;
            font-weight: 600;
        }
        tr:hover {
            background: #f8fafc;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-success {
            background: #dcfce7;
            color: #166534;
        }
        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
        }
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        .badge-info {
            background: #dbeafe;
            color: #1e40af;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-group textarea {
            min-height: 80px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        .btn-primary:hover {
            background: #2563eb;
        }
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        .btn-danger:hover {
            background: #dc2626;
        }
        .btn-warning {
            background: #f59e0b;
            color: white;
        }
        .btn-warning:hover {
            background: #d97706;
        }
        .btn-success {
            background: #22c55e;
            color: white;
        }
        .btn-success:hover {
            background: #16a34a;
        }
        .btn-sm {
            padding: 5px 12px;
            font-size: 0.8rem;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .filter-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .filter-bar select, .filter-bar input {
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        }
        .progress-bar-mini {
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-bar-mini div {
            height: 100%;
            background: #22c55e;
            border-radius: 4px;
            transition: width 0.3s;
        }
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            .admin-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
        @media (max-width: 480px) {
            .admin-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔧 Admin Dashboard</h1>
            <div>
                <span>Welcome, <?= htmlspecialchars($userName) ?></span>
                <a href="dashboard.php" style="margin-left:15px;">📊 Student View</a>
                <a href="logout.php" style="margin-left:15px;">🚪 Logout</a>
            </div>
        </header>

        <?php if (isset($success)): ?>
            <div class="alert alert-success"><?= $success ?></div>
        <?php endif; ?>
        <?php if (isset($error)): ?>
            <div class="alert alert-error"><?= $error ?></div>
        <?php endif; ?>

        <!-- Statistics Cards -->
        <div class="admin-grid">
            <div class="stat-card">
                <div class="number"><?= $stats['total_users'] ?></div>
                <div class="label">👥 Total Users</div>
            </div>
            <div class="stat-card">
                <div class="number"><?= $stats['total_courses'] ?></div>
                <div class="label">📚 Total Courses</div>
            </div>
            <div class="stat-card">
                <div class="number"><?= $stats['total_quizzes'] ?></div>
                <div class="label">❓ Total Questions</div>
            </div>
            <div class="stat-card">
                <div class="number"><?= $stats['total_attempts'] ?></div>
                <div class="label">📝 Total Attempts</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tab-container">
            <div class="tabs">
                <button class="tab-btn active" data-tab="questions">📝 Manage Questions</button>
                <button class="tab-btn" data-tab="history">📊 Test History</button>
                <button class="tab-btn" data-tab="analytics">📈 Analytics</button>
                <button class="tab-btn" data-tab="add">➕ Add Question</button>
            </div>

            <!-- Tab 1: Manage Questions -->
            <div id="questions" class="tab-content active">
                <h3>All Questions</h3>
                <div class="filter-bar">
                    <select id="filterCourse" onchange="filterQuestions()">
                        <option value="">All Courses</option>
                        <?php foreach ($courses as $course): ?>
                            <option value="<?= $course['id'] ?>"><?= htmlspecialchars($course['title']) ?></option>
                        <?php endforeach; ?>
                    </select>
                    <select id="filterDifficulty" onchange="filterQuestions()">
                        <option value="">All Difficulties</option>
                        <option value="1">⭐ Level 1</option>
                        <option value="2">⭐⭐ Level 2</option>
                        <option value="3">⭐⭐⭐ Level 3</option>
                        <option value="4">⭐⭐⭐⭐ Level 4</option>
                        <option value="5">⭐⭐⭐⭐⭐ Level 5</option>
                    </select>
                    <input type="text" id="filterSearch" placeholder="Search questions..." onkeyup="filterQuestions()">
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Question</th>
                                <th>Course</th>
                                <th>Module</th>
                                <th>Difficulty</th>
                                <th>Correct Answer</th>
                                <th>Points</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($questions as $q): ?>
                                <tr data-course="<?= $q['course_id'] ?>" data-difficulty="<?= $q['difficulty_level'] ?>">
                                    <td>#<?= $q['id'] ?></td>
                                    <td><?= htmlspecialchars(substr($q['question'], 0, 50)) ?>...</td>
                                    <td><?= htmlspecialchars($q['course_title'] ?? 'N/A') ?></td>
                                    <td><?= htmlspecialchars($q['module_title'] ?? 'N/A') ?></td>
                                    <td>
                                        <span class="badge badge-info">
                                            <?= str_repeat('⭐', $q['difficulty_level']) ?>
                                        </span>
                                    </td>
                                    <td><strong><?= $q['correct_answer'] ?></strong></td>
                                    <td><?= $q['points'] ?></td>
                                    <td>
                                        <button class="btn btn-warning btn-sm" onclick="editQuestion(<?= $q['id'] ?>)">✏️</button>
                                        <form method="POST" style="display:inline;" onsubmit="return confirm('Delete this question?')">
                                            <input type="hidden" name="quiz_id" value="<?= $q['id'] ?>">
                                            <button type="submit" name="delete_question" class="btn btn-danger btn-sm">🗑️</button>
                                        </form>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 2: Test History -->
            <div id="history" class="tab-content">
                <h3>Recent Test History</h3>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Email</th>
                                <th>Course</th>
                                <th>Question</th>
                                <th>Selected</th>
                                <th>Correct Answer</th>
                                <th>Result</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recentHistory as $h): ?>
                                <tr>
                                    <td><?= htmlspecialchars($h['full_name']) ?></td>
                                    <td><?= htmlspecialchars($h['email']) ?></td>
                                    <td><?= htmlspecialchars($h['course_title'] ?? 'N/A') ?></td>
                                    <td><?= htmlspecialchars(substr($h['question'], 0, 30)) ?>...</td>
                                    <td><?= $h['selected_answer'] ?? 'N/A' ?></td>
                                    <td><?= $h['correct_answer'] ?></td>
                                    <td>
                                        <span class="badge <?= $h['answered_correctly'] ? 'badge-success' : 'badge-danger' ?>">
                                            <?= $h['answered_correctly'] ? '✅ Correct' : '❌ Incorrect' ?>
                                        </span>
                                    </td>
                                    <td><?= date('Y-m-d H:i', strtotime($h['attempted_at'])) ?></td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 3: Analytics -->
            <div id="analytics" class="tab-content">
                <h3>Analytics Dashboard</h3>
                
                <!-- Course-wise Statistics -->
                <h4>📊 Course Performance</h4>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Course</th>
                                <th>Questions</th>
                                <th>Students</th>
                                <th>Attempts</th>
                                <th>Success Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($courseStats as $cs): ?>
                                <tr>
                                    <td><?= htmlspecialchars($cs['title']) ?></td>
                                    <td><?= $cs['total_questions'] ?></td>
                                    <td><?= $cs['unique_students'] ?></td>
                                    <td><?= $cs['total_attempts'] ?></td>
                                    <td>
                                        <?= $cs['avg_success_rate'] ?? 0 ?>%
                                        <div class="progress-bar-mini">
                                            <div style="width: <?= $cs['avg_success_rate'] ?? 0 ?>%;"></div>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <!-- User Performance -->
                <h4>👨‍🎓 Student Performance Ranking</h4>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Student</th>
                                <th>Email</th>
                                <th>Courses</th>
                                <th>Attempts</th>
                                <th>Correct</th>
                                <th>Success Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php 
                            $rank = 1;
                            foreach ($userPerformance as $up): 
                                if ($up['total_attempts'] == 0) continue;
                            ?>
                                <tr>
                                    <td>#<?= $rank++ ?></td>
                                    <td><?= htmlspecialchars($up['full_name']) ?></td>
                                    <td><?= htmlspecialchars($up['email']) ?></td>
                                    <td><?= $up['courses_attempted'] ?></td>
                                    <td><?= $up['total_attempts'] ?></td>
                                    <td><?= $up['correct_answers'] ?></td>
                                    <td>
                                        <?= $up['success_rate'] ?>%
                                        <div class="progress-bar-mini">
                                            <div style="width: <?= $up['success_rate'] ?>%;"></div>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <!-- Difficulty Distribution -->
                <h4>📊 Question Difficulty Distribution</h4>
                <div style="display:flex; gap:20px; flex-wrap:wrap; margin:15px 0;">
                    <?php foreach ($difficultyDistribution as $dd): ?>
                        <div style="flex:1; min-width:100px; background:#f8fafc; padding:15px; border-radius:10px; text-align:center;">
                            <div style="font-size:1.5rem; font-weight:bold;"><?= str_repeat('⭐', $dd['difficulty_level']) ?></div>
                            <div><?= $dd['count'] ?> questions</div>
                        </div>
                    <?php endforeach; ?>
                </div>

                <!-- Daily Activity -->
                <h4>📈 Daily Activity (Last 7 Days)</h4>
                <div style="display:flex; gap:10px; flex-wrap:wrap; margin:15px 0;">
                    <?php 
                    $maxAttempts = max(array_column($dailyActivity, 'attempts')) ?: 1;
                    foreach ($dailyActivity as $day): 
                        $height = ($day['attempts'] / $maxAttempts) * 100;
                    ?>
                        <div style="flex:1; min-width:40px; text-align:center; background:#f8fafc; padding:10px; border-radius:8px;">
                            <div style="display:flex; flex-direction:column; align-items:center;">
                                <div style="height:100px; display:flex; align-items:flex-end; width:30px;">
                                    <div style="height:<?= $height ?>%; background:#3b82f6; width:100%; border-radius:4px 4px 0 0;"></div>
                                </div>
                                <div style="font-size:0.7rem; margin-top:5px;"><?= date('D', strtotime($day['date'])) ?></div>
                                <div style="font-size:0.8rem; font-weight:bold;"><?= $day['attempts'] ?></div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>

            <!-- Tab 4: Add Question -->
            <div id="add" class="tab-content">
                <h3>➕ Add New Question</h3>
                <form method="POST" style="max-width:700px;">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Course *</label>
                            <select name="course_id" required>
                                <option value="">Select Course</option>
                                <?php foreach ($courses as $course): ?>
                                    <option value="<?= $course['id'] ?>"><?= htmlspecialchars($course['title']) ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Module</label>
                            <select name="module_id">
                                <option value="">Optional</option>
                                <?php foreach ($modules as $module): ?>
                                    <option value="<?= $module['id'] ?>"><?= htmlspecialchars($module['title']) ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Question *</label>
                        <textarea name="question" required placeholder="Enter your question here..."></textarea>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Option A *</label>
                            <input type="text" name="option_a" required>
                        </div>
                        <div class="form-group">
                            <label>Option B *</label>
                            <input type="text" name="option_b" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Option C *</label>
                            <input type="text" name="option_c" required>
                        </div>
                        <div class="form-group">
                            <label>Option D *</label>
                            <input type="text" name="option_d" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Correct Answer *</label>
                            <select name="correct_answer" required>
                                <option value="">Select</option>
                                <option value="A">A</option>
                                <option value="B">B</option>
                                <option value="C">C</option>
                                <option value="D">D</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Difficulty Level *</label>
                            <select name="difficulty" required>
                                <option value="1">⭐ Level 1 (Easy)</option>
                                <option value="2">⭐⭐ Level 2</option>
                                <option value="3">⭐⭐⭐ Level 3 (Medium)</option>
                                <option value="4">⭐⭐⭐⭐ Level 4</option>
                                <option value="5">⭐⭐⭐⭐⭐ Level 5 (Hard)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Topic</label>
                            <input type="text" name="topic" placeholder="e.g., Algebra, Physics">
                        </div>
                        <div class="form-group">
                            <label>Points</label>
                            <input type="number" name="points" value="10" min="1" max="100">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Time Limit (seconds)</label>
                        <input type="number" name="time_limit" value="30" min="10" max="300">
                    </div>
                    <button type="submit" name="add_question" class="btn btn-primary">📝 Add Question</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Edit Question Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>✏️ Edit Question</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <form method="POST" id="editForm">
                <input type="hidden" name="quiz_id" id="edit_quiz_id">
                <div class="form-group">
                    <label>Question *</label>
                    <textarea name="question" id="edit_question" required></textarea>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Option A *</label>
                        <input type="text" name="option_a" id="edit_option_a" required>
                    </div>
                    <div class="form-group">
                        <label>Option B *</label>
                        <input type="text" name="option_b" id="edit_option_b" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Option C *</label>
                        <input type="text" name="option_c" id="edit_option_c" required>
                    </div>
                    <div class="form-group">
                        <label>Option D *</label>
                        <input type="text" name="option_d" id="edit_option_d" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Correct Answer *</label>
                        <select name="correct_answer" id="edit_correct_answer" required>
                            <option value="A">A</option>
                            <option value="B">B</option>
                            <option value="C">C</option>
                            <option value="D">D</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Difficulty Level *</label>
                        <select name="difficulty" id="edit_difficulty" required>
                            <option value="1">⭐ Level 1</option>
                            <option value="2">⭐⭐ Level 2</option>
                            <option value="3">⭐⭐⭐ Level 3</option>
                            <option value="4">⭐⭐⭐⭐ Level 4</option>
                            <option value="5">⭐⭐⭐⭐⭐ Level 5</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Topic</label>
                        <input type="text" name="topic" id="edit_topic" placeholder="e.g., Algebra, Physics">
                    </div>
                    <div class="form-group">
                        <label>Points</label>
                        <input type="number" name="points" id="edit_points" min="1" max="100">
                    </div>
                </div>
                <button type="submit" name="update_question" class="btn btn-primary">💾 Update Question</button>
            </form>
        </div>
    </div>

    <script>
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                document.getElementById(this.dataset.tab).classList.add('active');
            });
        });

        // Filter questions
        function filterQuestions() {
            const course = document.getElementById('filterCourse').value;
            const difficulty = document.getElementById('filterDifficulty').value;
            const search = document.getElementById('filterSearch').value.toLowerCase();
            
            document.querySelectorAll('#questions tbody tr').forEach(row => {
                let show = true;
                if (course && row.dataset.course != course) show = false;
                if (difficulty && row.dataset.difficulty != difficulty) show = false;
                if (search && !row.textContent.toLowerCase().includes(search)) show = false;
                row.style.display = show ? '' : 'none';
            });
        }

        // Edit question
        function editQuestion(id) {
            fetch(`get_question.php?id=${id}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('edit_quiz_id').value = data.id;
                    document.getElementById('edit_question').value = data.question;
                    document.getElementById('edit_option_a').value = data.option_a;
                    document.getElementById('edit_option_b').value = data.option_b;
                    document.getElementById('edit_option_c').value = data.option_c;
                    document.getElementById('edit_option_d').value = data.option_d;
                    document.getElementById('edit_correct_answer').value = data.correct_answer;
                    document.getElementById('edit_difficulty').value = data.difficulty_level;
                    document.getElementById('edit_topic').value = data.topic || '';
                    document.getElementById('edit_points').value = data.points || 10;
                    document.getElementById('editModal').classList.add('active');
                })
                .catch(error => console.error('Error:', error));
        }

        function closeModal() {
            document.getElementById('editModal').classList.remove('active');
        }

        // Close modal on outside click
        document.getElementById('editModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    </script>
</body>
</html>