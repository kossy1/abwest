<?php
// dashboard.php - Student Dashboard
session_start();
require_once 'config.php';
require_once 'functions.php';

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

$userId = $_SESSION['user_id'];
$userName = $_SESSION['user_name'];

// Check if user is admin - redirect to admin dashboard if they are
if (isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'admin') {
    header('Location: admin_dashboard.php');
    exit;
}

$courses = getCourses();
$selectedCourse = isset($_GET['course_id']) ? $_GET['course_id'] : (isset($courses[0]['id']) ? $courses[0]['id'] : 0);
$quizzes = getQuizzesForCourse($selectedCourse, $userId);
$progress = getProgress($userId, $selectedCourse);
$courseName = getCourseName($selectedCourse);
$message = '';

// Handle quiz submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['answer'], $_POST['quiz_id'])) {
    $quizId = $_POST['quiz_id'];
    $answer = $_POST['answer'];
    $stmt = $pdo->prepare("SELECT correct_answer FROM quizzes WHERE id = ?");
    $stmt->execute([$quizId]);
    $correct = $stmt->fetchColumn();
    $isCorrect = ($answer === $correct);
    recordProgress($userId, $selectedCourse, $quizId, $isCorrect);
    
    if ($isCorrect) {
        $message = "✅ Correct! Well done!";
    } else {
        $message = "❌ Incorrect. The correct answer was " . strtoupper($correct) . ".";
    }
    
    // Refresh quizzes and progress
    $quizzes = getQuizzesForCourse($selectedCourse, $userId);
    $progress = getProgress($userId, $selectedCourse);
}

// Calculate overall progress
$totalProgress = 0;
$courseProgress = [];
foreach ($courses as $course) {
    $prog = getProgress($userId, $course['id']);
    $total = $prog['total'] > 0 ? min(100, ($prog['correct'] / max($prog['total'], 1)) * 100) : 0;
    $courseProgress[$course['id']] = $total;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Dashboard - Adaptive Learning</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Student Dashboard</h1>
            <div>
                <span>Welcome, <?= htmlspecialchars($userName) ?></span>
                <a href="logout.php" style="margin-left:15px;">🚪 Logout</a>
            </div>
        </header>

        <?php if ($message): ?>
            <div class="alert alert-info"><?= $message ?></div>
        <?php endif; ?>

        <div class="dashboard-grid">
            <!-- Sidebar with courses -->
            <aside class="course-list">
                <h3>Your Courses</h3>
                <ul>
                    <?php foreach ($courses as $course): ?>
                        <li>
                            <a href="?course_id=<?= $course['id'] ?>" class="<?= $course['id'] == $selectedCourse ? 'active' : '' ?>">
                                <?= htmlspecialchars($course['title']) ?>
                            </a>
                            <div class="progress-bar-mini">
                                <div style="width: <?= $courseProgress[$course['id']] ?>%;"></div>
                            </div>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </aside>

            <!-- Main quiz area -->
            <main class="quiz-area">
                <h2><?= htmlspecialchars($courseName) ?> - Adaptive Quiz</h2>
                
                <div class="progress-bar">
                    <span>Progress: <?= $progress['correct'] ?> / <?= $progress['total'] ?> correct</span>
                    <div class="bar">
                        <div style="width: <?= $progress['total'] > 0 ? ($progress['correct'] / $progress['total']) * 100 : 0 ?>%;"></div>
                    </div>
                </div>

                <?php if (empty($quizzes)): ?>
                    <div class="alert alert-success">
                        🎉 You've mastered this course! 
                        <br>Try another course or challenge yourself with more advanced questions.
                    </div>
                    
                    <!-- Show recommended advanced questions if any -->
                    <?php 
                    $advQuestions = getDifficultQuestions($userId, $selectedCourse, 3);
                    if (!empty($advQuestions)): 
                    ?>
                        <h3>Challenge Questions</h3>
                        <?php foreach ($advQuestions as $quiz): ?>
                            <div class="quiz-card">
                                <p><strong>Q:</strong> <?= htmlspecialchars($quiz['question']) ?></p>
                                <form method="POST" class="quiz-form">
                                    <input type="hidden" name="quiz_id" value="<?= $quiz['id'] ?>">
                                    <div class="options">
                                        <label><input type="radio" name="answer" value="A" required> A. <?= htmlspecialchars($quiz['option_a']) ?></label>
                                        <label><input type="radio" name="answer" value="B"> B. <?= htmlspecialchars($quiz['option_b']) ?></label>
                                        <label><input type="radio" name="answer" value="C"> C. <?= htmlspecialchars($quiz['option_c']) ?></label>
                                        <label><input type="radio" name="answer" value="D"> D. <?= htmlspecialchars($quiz['option_d']) ?></label>
                                    </div>
                                    <button type="submit">Submit Answer</button>
                                </form>
                            </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                    
                <?php else: ?>
                    <?php foreach ($quizzes as $quiz): ?>
                        <div class="quiz-card">
                            <p>
                                <strong>Q:</strong> <?= htmlspecialchars($quiz['question']) ?>
                                <span class="badge badge-info" style="margin-left:10px;">
                                    <?= str_repeat('⭐', $quiz['difficulty_level']) ?>
                                </span>
                            </p>
                            <form method="POST" class="quiz-form">
                                <input type="hidden" name="quiz_id" value="<?= $quiz['id'] ?>">
                                <div class="options">
                                    <label><input type="radio" name="answer" value="A" required> A. <?= htmlspecialchars($quiz['option_a']) ?></label>
                                    <label><input type="radio" name="answer" value="B"> B. <?= htmlspecialchars($quiz['option_b']) ?></label>
                                    <label><input type="radio" name="answer" value="C"> C. <?= htmlspecialchars($quiz['option_c']) ?></label>
                                    <label><input type="radio" name="answer" value="D"> D. <?= htmlspecialchars($quiz['option_d']) ?></label>
                                </div>
                                <button type="submit">Submit Answer</button>
                            </form>
                        </div>
                    <?php endforeach; ?>
                <?php endif; ?>
            </main>
        </div>
    </div>
</body>
</html>