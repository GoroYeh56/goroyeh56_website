<?php
/**
 * rss-proxy.php — Server-side RSS → JSON for goroyeh56.com
 * Fetches the WordPress feed locally (no third-party API, no rate limits)
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-cache, must-revalidate'); // always fetch fresh

$count = isset($_GET['count']) ? min((int)$_GET['count'], 20) : 6;

// Use WordPress REST API — always real-time, no feed cache
$api_url = 'https://goroyeh56.com/wp-json/wp/v2/posts?per_page=' . $count . '&_embed=1&orderby=date&order=desc';

$json_str = false;

if (function_exists('curl_init')) {
    $ch = curl_init($api_url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT        => 10,
        CURLOPT_USERAGENT      => 'Mozilla/5.0 (compatible; goroyeh56-proxy/1.0)',
        CURLOPT_SSL_VERIFYPEER => false,
    ]);
    $json_str = curl_exec($ch);
    curl_close($ch);
} else {
    $json_str = @file_get_contents($api_url);
}

if (!$json_str) {
    http_response_code(502);
    echo json_encode(['status' => 'error', 'message' => 'Could not reach WordPress API']);
    exit;
}

$posts = json_decode($json_str, true);

if (!is_array($posts)) {
    http_response_code(502);
    echo json_encode(['status' => 'error', 'message' => 'Invalid response from WordPress API']);
    exit;
}

$items = [];

foreach ($posts as $post) {
    // Featured image
    $thumbnail = '';
    if (!empty($post['_embedded']['wp:featuredmedia'][0]['source_url'])) {
        $thumbnail = $post['_embedded']['wp:featuredmedia'][0]['source_url'];
    }

    // Categories (names)
    $categories = [];
    if (!empty($post['_embedded']['wp:term'])) {
        foreach ($post['_embedded']['wp:term'] as $term_group) {
            foreach ($term_group as $term) {
                if ($term['taxonomy'] === 'category') {
                    $categories[] = $term['name'];
                }
            }
        }
    }

    // Word count for read time
    $content = strip_tags($post['content']['rendered'] ?? '');

    $items[] = [
        'title'       => html_entity_decode(strip_tags($post['title']['rendered']), ENT_QUOTES, 'UTF-8'),
        'link'        => $post['link'],
        'pubDate'     => $post['date'],
        'categories'  => $categories,
        'thumbnail'   => $thumbnail,
        'description' => substr(strip_tags($post['excerpt']['rendered'] ?? ''), 0, 200),
        'content'     => $content,
    ];
}

echo json_encode([
    'status' => 'ok',
    'feed'   => ['title' => 'Goro Yeh', 'link' => 'https://goroyeh56.com'],
    'items'  => $items,
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
