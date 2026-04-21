<?php
/**
 * photography-index.php
 *
 * Scans public_html/photography/ and returns a JSON list of images
 * for the gallery on index.html.
 *
 * Upload your photos to: public_html/photography/<filename>.<ext>
 * Supported formats: jpg, jpeg, png, webp, gif
 *
 * Optional metadata: create a file with the same base name + ".txt"
 * containing a single line caption.
 * e.g.  photography/sunset-yosemite.jpg
 *       photography/sunset-yosemite.txt  → "Golden hour, Yosemite 2024"
 *
 * Response format:
 * {
 *   "status": "ok",
 *   "photos": [
 *     { "thumb": "/photography/img.jpg",
 *       "full":  "/photography/img.jpg",
 *       "caption": "Optional caption",
 *       "filename": "img.jpg" }
 *   ]
 * }
 */

header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: public, max-age=300'); // 5-min browser cache

// ── Config ───────────────────────────────────────────────────────────────
$PHOTO_DIR  = __DIR__ . '/photography/';     // absolute path on disk
$PHOTO_URL  = '/photography/';               // public URL prefix
$EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
$MAX_PHOTOS = 24;
// ─────────────────────────────────────────────────────────────────────────

if (!is_dir($PHOTO_DIR)) {
    // Directory doesn't exist yet — return empty so proxy fallback kicks in
    echo json_encode(['status' => 'empty', 'photos' => []]);
    exit;
}

$files = [];
$dir   = new DirectoryIterator($PHOTO_DIR);
foreach ($dir as $file) {
    if ($file->isDot() || $file->isDir()) continue;
    $ext = strtolower($file->getExtension());
    if (!in_array($ext, $EXTENSIONS)) continue;
    $files[] = [
        'name'    => $file->getFilename(),
        'mtime'   => $file->getMTime(),
        'size'    => $file->getSize(),
    ];
}

if (empty($files)) {
    echo json_encode(['status' => 'empty', 'photos' => []]);
    exit;
}

// Sort: newest first (by file modification time)
usort($files, fn($a, $b) => $b['mtime'] - $a['mtime']);

// Slice to max
$files = array_slice($files, 0, $MAX_PHOTOS);

$photos = [];
foreach ($files as $f) {
    $filename = $f['name'];
    $url      = $PHOTO_URL . rawurlencode($filename);

    // Read optional caption from sidecar .txt file
    $base     = pathinfo($filename, PATHINFO_FILENAME);
    $sidecar  = $PHOTO_DIR . $base . '.txt';
    $caption  = '';
    if (file_exists($sidecar)) {
        $caption = trim(file_get_contents($sidecar));
    } else {
        // Humanize filename: remove extension, replace _ and - with spaces
        $caption = ucfirst(str_replace(['_', '-'], ' ', $base));
    }

    $photos[] = [
        'thumb'    => $url,   // same file used for both thumb and full
        'full'     => $url,   // (add separate /photography/thumbs/ later if needed)
        'caption'  => $caption,
        'filename' => $filename,
    ];
}

echo json_encode([
    'status' => 'ok',
    'count'  => count($photos),
    'photos' => $photos,
]);
