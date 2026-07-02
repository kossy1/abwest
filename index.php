<?php
// index.php - Main entry point with responsive layout
session_start();
require_once 'config.php';
require_once 'functions.php';

// Handle user login/signup
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['login'])) {
        $user = loginUser($_POST['email'], $_POST['password']);
        if ($user) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['user_name'] = $user['full_name'];
            $_SESSION['user_role'] = $user['role'];
            
            // Redirect based on role
            if ($user['role'] === 'admin') {
                header('Location: admin_dashboard.php');
            } else {
                header('Location: dashboard.php');
            }
            exit;
        } else {
            $error = "Invalid credentials";
        }
    } elseif (isset($_POST['signup'])) {
        if (registerUser($_POST['name'], $_POST['email'], $_POST['password'])) {
            $success = "Account created! Please login.";
        } else {
            $error = "Signup failed. Email may already exist.";
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive Learning Platform</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Adaptive Learning Platform</h1>
            <p>Dynamic Quizzes & Real-Time Progress Tracking</p>
        </header>

        <?php if (isset($error)): ?>
            <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>
        <?php if (isset($success)): ?>
            <div class="alert alert-success"><?= htmlspecialchars($success) ?></div>
        <?php endif; ?>

        <div class="auth-forms">
            <div class="form-card">
                <h2>Login</h2>
                <form method="POST">
                    <input type="email" name="email" placeholder="Email" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit" name="login">Login</button>
                </form>
                <p style="margin-top:10px; font-size:0.8rem; color:#64748b;">
                    Demo: student@example.com / student123<br>
                    Admin: admin@example.com / admin123
                </p>
            </div>
            <div class="form-card">
                <h2>Sign Up</h2>
                <form method="POST">
                    <input type="text" name="name" placeholder="Full Name" required>
                    <input type="email" name="email" placeholder="Email" required>
                    <input type="password" name="password" placeholder="Password (min 6 chars)" required>
                    <button type="submit" name="signup">Create Account</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>