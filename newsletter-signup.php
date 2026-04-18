<?php
/**
 * newsletter-signup.php
 * Handles email signups from ml-starter-kit.html
 *
 * Setup options (choose ONE):
 *   A) Simple: save to CSV + send welcome email via PHP mail()
 *   B) Mailchimp API  — set MAILCHIMP_API_KEY + MAILCHIMP_LIST_ID
 *   C) ConvertKit API — set CONVERTKIT_API_KEY + CONVERTKIT_FORM_ID
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://goroyeh56.com');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit(0); }
if ($_SERVER['REQUEST_METHOD'] !== 'POST')    { http_response_code(405); echo json_encode(['error'=>'Method not allowed']); exit; }

// ── Config ───────────────────────────────────────────────────────────────
$YOUR_EMAIL      = 'goroyeh56@gmail.com';       // <-- your email
$CSV_FILE        = __DIR__ . '/data/subscribers.csv';
$FROM_NAME       = 'Goro Yeh';
$FROM_EMAIL      = 'noreply@goroyeh56.com';

// Optional: Mailchimp
$MAILCHIMP_API_KEY  = '';   // e.g. 'abc123-us1'
$MAILCHIMP_LIST_ID  = '';   // e.g. 'a1b2c3d4e5'
$MAILCHIMP_SERVER   = '';   // e.g. 'us1' (last part of API key after dash)

// Optional: ConvertKit
$CONVERTKIT_API_KEY = '';
$CONVERTKIT_FORM_ID = '';
// ─────────────────────────────────────────────────────────────────────────

// Parse body
$body  = json_decode(file_get_contents('php://input'), true);
$email = trim(filter_var($body['email'] ?? '', FILTER_SANITIZE_EMAIL));
$source = trim(strip_tags($body['source'] ?? 'ml-starter-kit'));

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid email address']);
    exit;
}

// ── Option A: Save to CSV ────────────────────────────────────────────────
$dir = dirname($CSV_FILE);
if (!is_dir($dir)) mkdir($dir, 0755, true);
$exists = file_exists($CSV_FILE);
$fp = fopen($CSV_FILE, 'a');
if ($fp) {
    if (!$exists) fputcsv($fp, ['email', 'source', 'subscribed_at', 'ip']);
    fputcsv($fp, [
        $email,
        $source,
        date('Y-m-d H:i:s'),
        $_SERVER['REMOTE_ADDR'] ?? '',
    ]);
    fclose($fp);
}

// ── Option B: Mailchimp ──────────────────────────────────────────────────
if ($MAILCHIMP_API_KEY && $MAILCHIMP_LIST_ID) {
    $url = "https://{$MAILCHIMP_SERVER}.api.mailchimp.com/3.0/lists/{$MAILCHIMP_LIST_ID}/members";
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_USERPWD => "anystring:{$MAILCHIMP_API_KEY}",
        CURLOPT_POSTFIELDS => json_encode([
            'email_address' => $email,
            'status' => 'subscribed',
            'tags'   => [$source],
        ]),
    ]);
    curl_exec($ch);
    curl_close($ch);
}

// ── Option C: ConvertKit ─────────────────────────────────────────────────
if ($CONVERTKIT_API_KEY && $CONVERTKIT_FORM_ID) {
    $url = "https://api.convertkit.com/v3/forms/{$CONVERTKIT_FORM_ID}/subscribe";
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => json_encode([
            'api_key' => $CONVERTKIT_API_KEY,
            'email'   => $email,
        ]),
    ]);
    curl_exec($ch);
    curl_close($ch);
}

// ── Welcome email ────────────────────────────────────────────────────────
$subject = 'Your free AV Perception Starter Kit is here';
$message = <<<HTML
Hi,

Welcome — your download is ready.

── DOWNLOAD LINKS ──────────────────────────────────────
ZIP archive:   https://goroyeh56.com/downloads/av-perception-kit.zip
GitHub repo:   https://github.com/goroyeh56/av-perception-kit
ML Roadmap:    https://goroyeh56.com/ml-roadmap.html
────────────────────────────────────────────────────────

The ZIP includes:
• 12 weeks of Python code (numpy, PyTorch, Open3D)
• Docker / Conda environment configs
• Waymo + NuScenes dataset parsing scripts
• The pitfall guide — mistakes I made so you don't have to

Start with week01_linear_algebra.py and run:
  docker-compose up
  # or: conda env create -f environment.yml

If you hit a specific technical wall after working through the material,
you can request a 15-minute office hours slot at:
https://goroyeh56.com/office-hours.html

— Goro
goroyeh56.com

--
Unsubscribe: reply with "unsubscribe" in the subject line.
HTML;

$headers  = "From: {$FROM_NAME} <{$FROM_EMAIL}>\r\n";
$headers .= "Reply-To: {$FROM_EMAIL}\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

mail($email, $subject, $message, $headers);

// Notify yourself
mail($YOUR_EMAIL, "[goroyeh56] New subscriber: {$email}", "Source: {$source}\nEmail: {$email}\nTime: ".date('Y-m-d H:i:s'), $headers);

echo json_encode(['success' => true, 'message' => 'Subscribed successfully']);
