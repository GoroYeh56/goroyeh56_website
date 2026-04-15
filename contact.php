<?php
/**
 * contact.php — Contact form handler for goroyeh56.com
 * Bluehost shared hosting compatible
 */

header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

// ── CONFIG ─────────────────────────────────────────────
$TO_EMAIL   = 'goroyeh56@gmail.com';   // ← Change to your email
$FROM_EMAIL = 'noreply@goroyeh56.com'; // ← Your domain email
$SITE_NAME  = 'goroyeh56.com';
// ───────────────────────────────────────────────────────

// Sanitize helpers
function clean(string $val): string {
    return htmlspecialchars(strip_tags(trim($val)), ENT_QUOTES, 'UTF-8');
}

// Rate limiting via session (basic)
session_start();
$now = time();
if (!isset($_SESSION['last_contact'])) $_SESSION['last_contact'] = 0;
if ($now - $_SESSION['last_contact'] < 60) {
    http_response_code(429);
    echo json_encode(['success' => false, 'message' => 'Please wait a moment before sending again.']);
    exit;
}

// Validate inputs
$name    = clean($_POST['name']    ?? '');
$email   = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$message = clean($_POST['message'] ?? '');

if (!$name || strlen($name) < 2) {
    echo json_encode(['success' => false, 'message' => 'Please enter your name.']);
    exit;
}
if (!$email) {
    echo json_encode(['success' => false, 'message' => 'Please enter a valid email.']);
    exit;
}
if (!$message || strlen($message) < 10) {
    echo json_encode(['success' => false, 'message' => 'Message too short. Please write at least 10 characters.']);
    exit;
}

// Honeypot check (add hidden field "website" in form for bots)
if (!empty($_POST['website'])) {
    echo json_encode(['success' => true, 'message' => 'Message sent!']); // silent discard
    exit;
}

// Build email
$subject = "New message from {$name} via {$SITE_NAME}";
$body = "You have a new contact form submission from {$SITE_NAME}.\n\n"
      . "Name:    {$name}\n"
      . "Email:   {$email}\n"
      . "Time:    " . date('Y-m-d H:i:s T') . "\n\n"
      . "Message:\n"
      . str_repeat('-', 40) . "\n"
      . wordwrap($message, 72, "\n", true) . "\n"
      . str_repeat('-', 40) . "\n\n"
      . "Reply directly to this email or to: {$email}";

$headers  = "From: {$SITE_NAME} <{$FROM_EMAIL}>\r\n";
$headers .= "Reply-To: {$name} <{$email}>\r\n";
$headers .= "X-Mailer: PHP/" . PHP_VERSION . "\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

// Send
$sent = mail($TO_EMAIL, $subject, $body, $headers);

if ($sent) {
    $_SESSION['last_contact'] = $now;
    echo json_encode(['success' => true, 'message' => 'Message sent successfully!']);
} else {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Failed to send. Please try again.']);
}
