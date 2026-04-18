<?php
/**
 * office-hours-apply.php
 * Receives office hours applications from office-hours.html
 * Saves to CSV and notifies you by email.
 *
 * You review manually and send the Calendly link yourself.
 * If you want auto-scoring and auto-send, set $AUTO_RESPOND = true.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://goroyeh56.com');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit(0); }
if ($_SERVER['REQUEST_METHOD'] !== 'POST')    { http_response_code(405); exit; }

// ── Config ───────────────────────────────────────────────────────────────
$YOUR_EMAIL    = 'goroyeh56@gmail.com';         // <-- your email
$FROM_EMAIL    = 'noreply@goroyeh56.com';
$CALENDLY_LINK = 'https://calendly.com/goroyeh56/15min'; // <-- your Calendly URL
$CSV_FILE      = __DIR__ . '/data/office-hours-applications.csv';
$AUTO_RESPOND  = true;   // true = send email immediately; false = you send manually
// ─────────────────────────────────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true);

// Sanitize
$name     = strip_tags(trim($body['name']     ?? ''));
$email    = filter_var(trim($body['email']    ?? ''), FILTER_SANITIZE_EMAIL);
$role     = strip_tags(trim($body['role']     ?? ''));
$question = strip_tags(trim($body['question'] ?? ''));
$tried    = strip_tags(trim($body['tried']    ?? ''));
$topic    = strip_tags(trim($body['topic']    ?? ''));
$success  = strip_tags(trim($body['success']  ?? ''));
$link     = filter_var(trim($body['link']     ?? ''), FILTER_SANITIZE_URL);
$score    = (int)($body['score'] ?? 0);

if (!filter_var($email, FILTER_VALIDATE_EMAIL) || empty($question)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields']);
    exit;
}

$accepted = $score >= 55;

// ── Save to CSV ──────────────────────────────────────────────────────────
$dir = dirname($CSV_FILE);
if (!is_dir($dir)) mkdir($dir, 0755, true);
$exists = file_exists($CSV_FILE);
$fp = fopen($CSV_FILE, 'a');
if ($fp) {
    if (!$exists) fputcsv($fp, ['name','email','role','question','tried','topic','success','link','score','accepted','submitted_at','ip']);
    fputcsv($fp, [$name,$email,$role,$question,$tried,$topic,$success,$link,$score,$accepted?'YES':'NO',date('Y-m-d H:i:s'),$_SERVER['REMOTE_ADDR']??'']);
    fclose($fp);
}

// ── Notify yourself ──────────────────────────────────────────────────────
$notif = <<<TXT
New Office Hours Application
Score: {$score}/100 — {$accepted ? 'ACCEPTED' : 'DECLINED'}
────────────────────────────
Name:     {$name}
Email:    {$email}
Role:     {$role}
Topic:    {$topic}
Score:    {$score}/100

Question:
{$question}

What they tried:
{$tried}

Success looks like:
{$success}

Code link: {$link}
────────────────────────────
Reply to {$email} with the Calendly link if you want to proceed.
TXT;

$headers  = "From: Office Hours Bot <{$FROM_EMAIL}>\r\n";
$headers .= "Reply-To: {$email}\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
mail($YOUR_EMAIL, "[OH App] {$accepted?'✓ ACCEPTED':'→ DECLINED'} — {$name} (score:{$score})", $notif, $headers);

// ── Auto-respond to applicant ────────────────────────────────────────────
if ($AUTO_RESPOND) {
    $applicantHeaders  = "From: Goro Yeh <{$FROM_EMAIL}>\r\n";
    $applicantHeaders .= "Reply-To: {$FROM_EMAIL}\r\n";
    $applicantHeaders .= "Content-Type: text/plain; charset=UTF-8\r\n";

    if ($accepted) {
        $subject = 'Office Hours — you\'re in';
        $msg = <<<TXT
Hi {$name},

Your application came through with a specific question and clear context — exactly what makes these conversations useful.

Book your 15 minutes here:
{$CALENDLY_LINK}

A few things before we meet:
• Have your code or diagram open and ready to share at the start of the call
• We'll spend the first 2 minutes on context, then get to your specific problem
• If I don't know the answer, I'll say so — no filler

See you then.

— Goro
goroyeh56.com
TXT;
    } else {
        $subject = 'Office Hours — not a great fit right now';
        $msg = <<<TXT
Hi {$name},

Thanks for the application. Based on what you described, I think you'll get more value from working through the existing resources before we talk — a 15-minute conversation is most useful once you've hit a specific wall that the docs don't cover.

Start here:

ML Roadmap (interactive code for every topic):
https://goroyeh56.com/ml-roadmap.html

Free 12-Week AV Perception Kit (Docker + dataset scripts):
https://goroyeh56.com/ml-starter-kit.html

Field notes on the blog:
https://goroyeh56.com/blog

Once you've worked through the relevant section and hit a specific technical problem, apply again — I'm happy to help at that point.

— Goro
goroyeh56.com
TXT;
    }

    mail($email, $subject, $msg, $applicantHeaders);
}

echo json_encode(['success' => true, 'accepted' => $accepted, 'score' => $score]);
