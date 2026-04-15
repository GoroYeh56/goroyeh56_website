<?php
/**
 * photo-proxy.php — 從 WordPress 抓取 Photography & Travel 的照片
 * 自動更新首頁 photo grid，永遠顯示最新作品
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-cache, must-revalidate');

$count = isset($_GET['count']) ? min((int)$_GET['count'], 40) : 12;

function wp_fetch($url) {
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT        => 10,
            CURLOPT_USERAGENT      => 'Mozilla/5.0 (compatible; goroyeh56-photo-proxy/1.0)',
            CURLOPT_SSL_VERIFYPEER => false,
        ]);
        $result = curl_exec($ch);
        curl_close($ch);
        return $result;
    }
    return @file_get_contents($url);
}

$photos = [];

// ── Strategy 1: Get posts from "Photography and Travel" category with featured images
$cat_url = 'https://goroyeh56.com/wp-json/wp/v2/categories?slug=photography-and-travel&_fields=id';
$cat_json = wp_fetch($cat_url);
$cats = json_decode($cat_json, true);

if (!empty($cats) && isset($cats[0]['id'])) {
    $cat_id   = $cats[0]['id'];
    $posts_url = "https://goroyeh56.com/wp-json/wp/v2/posts?categories={$cat_id}&per_page=20&_embed=1&_fields=id,title,link,_embedded";
    $posts_json = wp_fetch($posts_url);
    $posts = json_decode($posts_json, true);

    if (is_array($posts)) {
        foreach ($posts as $post) {
            if (count($photos) >= $count) break;
            $media = $post['_embedded']['wp:featuredmedia'][0] ?? null;
            if ($media && !empty($media['source_url'])) {
                // Get medium_large size for grid, full for lightbox
                $sizes    = $media['media_details']['sizes'] ?? [];
                $thumb    = $sizes['medium_large']['source_url']
                         ?? $sizes['large']['source_url']
                         ?? $sizes['medium']['source_url']
                         ?? $media['source_url'];
                $photos[] = [
                    'thumb'   => $thumb,
                    'full'    => $media['source_url'],
                    'caption' => html_entity_decode(strip_tags($post['title']['rendered']), ENT_QUOTES, 'UTF-8'),
                    'link'    => $post['link'],
                    'type'    => 'post',
                ];
            }
        }
    }
}

// ── Strategy 2: If we don't have enough, pull directly from Media Library
// filtered by images uploaded in the past year
if (count($photos) < $count) {
    $needed    = $count - count($photos);
    $media_url = "https://goroyeh56.com/wp-json/wp/v2/media?media_type=image&per_page={$needed}&orderby=date&order=desc&_fields=id,source_url,alt_text,media_details,link";
    $media_json = wp_fetch($media_url);
    $media_items = json_decode($media_json, true);

    if (is_array($media_items)) {
        foreach ($media_items as $item) {
            if (count($photos) >= $count) break;
            if (empty($item['source_url'])) continue;

            // Skip small images (icons, avatars, thumbnails < 400px)
            $w = $item['media_details']['width']  ?? 0;
            $h = $item['media_details']['height'] ?? 0;
            if ($w < 400 || $h < 400) continue;

            $sizes = $item['media_details']['sizes'] ?? [];
            $thumb = $sizes['medium_large']['source_url']
                  ?? $sizes['large']['source_url']
                  ?? $sizes['medium']['source_url']
                  ?? $item['source_url'];

            $photos[] = [
                'thumb'   => $thumb,
                'full'    => $item['source_url'],
                'caption' => $item['alt_text'] ?: '',
                'link'    => '',
                'type'    => 'media',
            ];
        }
    }
}

// ── Strategy 3: Hardcoded fallback from portfolio page (always works)
if (count($photos) < 4) {
    $fallback = [
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07611-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07611-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07523-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07523-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07932-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC07932-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC09135-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC09135-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08460-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08460-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08306-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08306-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC09163-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC09163-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
        ['thumb' => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08709-scaled.jpg?resize=600%2C400&ssl=1',
         'full'  => 'https://i0.wp.com/goroyeh56.com/wp-content/uploads/2026/03/DSC08709-scaled.jpg?ssl=1',
         'caption' => 'Photography · 2026', 'link' => '', 'type' => 'fallback'],
    ];
    $photos = array_merge($photos, array_slice($fallback, 0, $count - count($photos)));
}

echo json_encode([
    'status' => 'ok',
    'count'  => count($photos),
    'photos' => array_slice($photos, 0, $count),
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
