"""
Stream URL Finder - Scans websites to find live video stream URLs
Supports: HLS (.m3u8), RTMP, DASH (.mpd), and more
Now with Selenium support for JavaScript-rendered content!
"""

import re
import json
import requests
import threading
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from urllib.parse import urljoin, urlparse

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def stream_finder_page(request):
    """Render the stream finder tool page"""
    return render(request, 'sleekweb/client/stream_finder.html')


@csrf_exempt
def scan_url(request):
    """
    API endpoint to scan a URL for video streams
    POST: { "url": "https://example.com", "use_selenium": true, "deep_scan": false }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        target_url = data.get('url', '').strip()
        use_selenium = data.get('use_selenium', False)
        deep_scan = data.get('deep_scan', False)  # Deep scan mode - waits longer, clicks more
        
        if not target_url:
            return JsonResponse({'error': 'URL is required'}, status=400)
        
        # Add https if missing
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
        
        # Choose scanning method
        if use_selenium:
            if not SELENIUM_AVAILABLE:
                return JsonResponse({
                    'error': 'Selenium not installed. Run: pip install selenium webdriver-manager'
                }, status=400)
            
            html_content, network_urls, js_sources = fetch_with_selenium(target_url, deep_scan=deep_scan)
        else:
            html_content = fetch_with_requests(target_url)
            network_urls = []
            js_sources = []
        
        if html_content is None:
            return JsonResponse({'error': 'Cannot fetch URL'}, status=400)
        
        # Find all stream URLs
        streams = find_stream_urls(html_content, base_url, target_url)
        
        # Add network captured URLs (from Selenium)
        for url in network_urls:
            if url not in [s['url'] for s in streams]:
                stream_type = detect_stream_type(url)
                if stream_type:
                    streams.append({
                        'url': url,
                        'type': stream_type,
                        'source': 'network_capture'
                    })
        
        # Parse JS sources for URLs
        for js_content in js_sources:
            js_streams = find_urls_in_js(js_content, base_url)
            for stream in js_streams:
                if stream['url'] not in [s['url'] for s in streams]:
                    streams.append(stream)
        
        # ========== FILTER: ONLY HLS (.m3u8) STREAMS ==========
        # Remove TS segments, iframes, and other non-HLS streams
        hls_streams = []
        for stream in streams:
            url_lower = stream['url'].lower()
            # Only keep .m3u8 URLs
            if '.m3u8' in url_lower:
                # Skip tracking/analytics URLs
                if 'ping.gif' in url_lower or 'analytics' in url_lower or 'tracking' in url_lower:
                    continue
                hls_streams.append(stream)
        
        streams = hls_streams
        
        # Check which streams are alive
        live_streams = []
        for stream in streams:
            status = check_stream_status(stream['url'])
            stream['status'] = status
            stream['status_text'] = 'Online' if status else 'Offline/Unknown'
            live_streams.append(stream)
        
        # Sort: online first
        live_streams.sort(key=lambda x: (not x['status'], x['type']))
        
        return JsonResponse({
            'success': True,
            'url': target_url,
            'method': 'selenium' if use_selenium else 'requests',
            'streams': live_streams,
            'total': len(live_streams),
            'online': sum(1 for s in live_streams if s['status'])
        })
        
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Request timeout - website too slow'}, status=408)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Cannot fetch URL: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


def fetch_with_requests(target_url):
    """Simple fetch using requests library"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    response = requests.get(target_url, headers=headers, timeout=15, verify=False)
    response.raise_for_status()
    return response.text


def fetch_with_selenium(target_url, deep_scan=False):
    """
    Fetch page with Selenium to execute JavaScript
    Returns: (html_content, captured_network_urls, js_sources)
    Enhanced: Clicks on channel tabs, waits longer, captures from multiple players
    
    Args:
        target_url: URL to scan
        deep_scan: If True, waits longer and clicks more aggressively (slower but more thorough)
    """
    captured_urls = []
    js_sources = []
    
    # Timing settings based on scan mode
    initial_wait = 12 if deep_scan else 8
    element_wait = 20 if deep_scan else 15
    post_element_wait = 8 if deep_scan else 5
    click_wait = 5 if deep_scan else 3
    js_click_wait = 4 if deep_scan else 2
    final_wait = 10 if deep_scan else 5
    
    # Setup Chrome options
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless=new')  # New headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')
    
    # Enable performance logging to capture network requests
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = None
    try:
        # Initialize driver with auto-managed chromedriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(45 if deep_scan else 30)
        
        # Navigate to page
        driver.get(target_url)
        
        # Wait for initial page load
        time.sleep(initial_wait)
        
        # Capture initial network logs
        capture_network_logs(driver, captured_urls)
        
        # Try to wait for video elements
        try:
            WebDriverWait(driver, element_wait).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
        except:
            pass  # No video element, continue anyway
        
        # Additional wait for dynamic content
        time.sleep(post_element_wait)
        
        # Capture network after initial load
        capture_network_logs(driver, captured_urls)
        try_get_jw_sources(driver, js_sources)
        
        # ========== CLICK ON CHANNEL TABS TO LOAD ALL PLAYERS ==========
        # Try to find and click on channel buttons/tabs to trigger loading of different streams
        channel_selectors = [
            # Common patterns for channel buttons
            '[data-channel]',
            '.channel-btn',
            '.channel-button',
            '.tab-btn',
            '.nav-tab',
            '.stream-tab',
            'button[onclick*="channel"]',
            'a[onclick*="channel"]',
            'button[onclick*="stream"]',
            'a[onclick*="stream"]',
            'button[onclick*="load"]',
            'a[onclick*="load"]',
            # Specific to many streaming sites
            '.c1, .c2, .c3, .c4, .c5',
            '[data-id="c1"], [data-id="c2"], [data-id="c3"], [data-id="c4"]',
            '[data-tab]',
            '[data-target]',
            '.nav-link',
            '.tab-link',
            # Try any clickable with channel/stream related text
            'button',
            'a.btn',
        ]
        
        clicked_tabs = set()
        max_elements_per_selector = 15 if deep_scan else 10
        
        for selector in channel_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements[:max_elements_per_selector]:
                    try:
                        elem_text = (elem.text.strip() if elem.text else '').lower()
                        elem_id = elem.get_attribute('id') or ''
                        elem_class = elem.get_attribute('class') or ''
                        elem_key = f"{elem_text}_{elem_id}_{elem_class}"
                        
                        # Filter for likely channel buttons
                        is_channel_button = any(keyword in elem_text or keyword in elem_class.lower() or keyword in elem_id.lower() 
                                               for keyword in ['c1', 'c2', 'c3', 'c4', 'c5', 'thomo', 'channel', 'stream', 'live', 'tab', 'dự phòng', 'du phong'])
                        
                        if deep_scan:
                            # In deep scan, click on more buttons
                            is_channel_button = is_channel_button or len(elem_text) < 20  # Short text buttons
                        
                        if elem_key not in clicked_tabs and elem.is_displayed() and is_channel_button:
                            clicked_tabs.add(elem_key)
                            driver.execute_script("arguments[0].click();", elem)
                            time.sleep(click_wait)
                            
                            # Capture network logs after each click
                            capture_network_logs(driver, captured_urls)
                            
                            # Try to get JW Player source after each click
                            try_get_jw_sources(driver, js_sources)
                            
                    except Exception as e:
                        continue
            except:
                continue
        
        # ========== TRY JAVASCRIPT CLICKS FOR COMMON PATTERNS ==========
        try:
            # Click on elements by text content
            click_scripts = [
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.trim().match(/^C1$/i)) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.trim().match(/^C2$/i)) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.trim().match(/^C3$/i)) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.trim().match(/^C4$/i)) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.trim().match(/^C5$/i)) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.includes('THOMO')) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.includes('Tonhon')) { e.click(); }});",
                "document.querySelectorAll('button, a, div[onclick]').forEach(function(e) { if(e.textContent.includes('Dự phòng')) { e.click(); }});",
            ]
            
            if deep_scan:
                # Add more patterns for deep scan
                click_scripts.extend([
                    "document.querySelectorAll('button, a').forEach(function(e) { if(e.textContent.includes('Live')) { e.click(); }});",
                    "document.querySelectorAll('button, a').forEach(function(e) { if(e.textContent.includes('Stream')) { e.click(); }});",
                    "document.querySelectorAll('button, a').forEach(function(e) { if(e.textContent.includes('Play')) { e.click(); }});",
                ])
            
            for script in click_scripts:
                try:
                    driver.execute_script(script)
                    time.sleep(js_click_wait)
                    capture_network_logs(driver, captured_urls)
                    try_get_jw_sources(driver, js_sources)
                except:
                    pass
        except:
            pass
        
        # Final wait for any remaining async content
        time.sleep(final_wait)
        
        # Get page source after JS execution
        html_content = driver.page_source
        
        # Final network log capture - do it multiple times to ensure we get everything
        for _ in range(3):
            capture_network_logs(driver, captured_urls)
            time.sleep(1)
        
        # ========== EXTRACT FROM ALL JW PLAYER INSTANCES ==========
        try:
            all_jw_sources = driver.execute_script("""
                var sources = [];
                if (typeof jwplayer === 'function') {
                    // Try to get all player instances
                    try {
                        var players = jwplayer.getPlayers ? jwplayer.getPlayers() : [];
                        if (Array.isArray(players)) {
                            players.forEach(function(p) {
                                try {
                                    var playlist = p.getPlaylist();
                                    if (playlist) sources.push(JSON.stringify(playlist));
                                    var config = p.getConfig();
                                    if (config && config.file) sources.push(config.file);
                                    if (config && config.sources) sources.push(JSON.stringify(config.sources));
                                } catch(e) {}
                            });
                        }
                    } catch(e) {}
                    
                    // Try default player
                    try {
                        var player = jwplayer();
                        if (player && player.getPlaylist) {
                            var playlist = player.getPlaylist();
                            if (playlist) sources.push(JSON.stringify(playlist));
                        }
                        if (player && player.getConfig) {
                            var config = player.getConfig();
                            if (config && config.file) sources.push(config.file);
                        }
                    } catch(e) {}
                    
                    // Try numbered player instances
                    for (var i = 0; i < 10; i++) {
                        try {
                            var playerId = 'jwplayer_' + i;
                            var playerEl = document.getElementById(playerId);
                            if (playerEl) {
                                var p = jwplayer(playerId);
                                if (p && p.getPlaylist) {
                                    sources.push(JSON.stringify(p.getPlaylist()));
                                }
                            }
                        } catch(e) {}
                    }
                    
                    // Try all video containers
                    document.querySelectorAll('[id*="player"], [id*="video"], [class*="player"], [class*="video"]').forEach(function(el) {
                        try {
                            var p = jwplayer(el);
                            if (p && p.getPlaylist) {
                                sources.push(JSON.stringify(p.getPlaylist()));
                            }
                        } catch(e) {}
                    });
                }
                return sources;
            """)
            if all_jw_sources:
                for src in all_jw_sources:
                    if src:
                        js_sources.append(src)
        except Exception as e:
            print(f"Error getting JW sources: {e}")
        
        # ========== TRY VIDEO.JS ==========
        try:
            videojs_src = driver.execute_script("""
                var sources = [];
                if (typeof videojs === 'function') {
                    try {
                        var players = document.querySelectorAll('.video-js');
                        players.forEach(function(p) {
                            try {
                                var player = videojs(p);
                                if (player && player.currentSrc) {
                                    sources.push(player.currentSrc());
                                }
                                if (player && player.src) {
                                    var src = player.src();
                                    if (typeof src === 'string') sources.push(src);
                                    if (Array.isArray(src)) sources = sources.concat(src.map(s => s.src));
                                }
                            } catch(e) {}
                        });
                    } catch(e) {}
                }
                return JSON.stringify(sources);
            """)
            if videojs_src:
                js_sources.append(videojs_src)
        except:
            pass
        
        # ========== TRY HLS.JS ==========
        try:
            hls_src = driver.execute_script("""
                var sources = [];
                // Get all video sources
                document.querySelectorAll('video').forEach(function(v) {
                    if (v.src) sources.push(v.src);
                    if (v.currentSrc) sources.push(v.currentSrc);
                    // Check for HLS attached
                    if (v.hls && v.hls.url) sources.push(v.hls.url);
                });
                // Check for global HLS instances
                if (typeof window.hlsPlayers !== 'undefined') {
                    window.hlsPlayers.forEach(function(h) {
                        if (h.url) sources.push(h.url);
                    });
                }
                return JSON.stringify(sources);
            """)
            if hls_src:
                js_sources.append(hls_src)
        except:
            pass
        
        # ========== GET ALL VIDEO SOURCES DIRECTLY ==========
        try:
            video_sources = driver.execute_script("""
                var sources = [];
                var videos = document.querySelectorAll('video, source, iframe');
                videos.forEach(function(v) {
                    if (v.src) sources.push(v.src);
                    if (v.currentSrc) sources.push(v.currentSrc);
                    if (v.getAttribute('data-src')) sources.push(v.getAttribute('data-src'));
                    if (v.getAttribute('data-file')) sources.push(v.getAttribute('data-file'));
                    if (v.getAttribute('data-stream')) sources.push(v.getAttribute('data-stream'));
                });
                return JSON.stringify(sources);
            """)
            if video_sources:
                js_sources.append(video_sources)
        except:
            pass
        
        # ========== EXTRACT JAVASCRIPT FROM SCRIPT TAGS ==========
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        for script in scripts:
            try:
                src = script.get_attribute('src')
                if src:
                    # Fetch external JS file
                    try:
                        js_response = requests.get(src, timeout=5, verify=False)
                        if js_response.status_code == 200:
                            js_sources.append(js_response.text)
                    except:
                        pass
                else:
                    # Inline script
                    content = script.get_attribute('innerHTML')
                    if content and len(content) < 500000:  # Skip very large scripts
                        js_sources.append(content)
            except:
                continue
        
        return html_content, list(set(captured_urls)), js_sources
        
    except Exception as e:
        print(f"Selenium error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to requests
        try:
            html = fetch_with_requests(target_url)
            return html, [], []
        except:
            return None, [], []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def capture_network_logs(driver, captured_urls):
    """Capture network logs and add stream URLs to list"""
    try:
        logs = driver.get_log('performance')
        for log in logs:
            try:
                message = json.loads(log['message'])['message']
                if message.get('method') == 'Network.requestWillBeSent':
                    url = message.get('params', {}).get('request', {}).get('url', '')
                    if url and is_stream_url(url) and url not in captured_urls:
                        captured_urls.append(url)
                elif message.get('method') == 'Network.responseReceived':
                    url = message.get('params', {}).get('response', {}).get('url', '')
                    if url and is_stream_url(url) and url not in captured_urls:
                        captured_urls.append(url)
            except:
                continue
    except:
        pass


def try_get_jw_sources(driver, js_sources):
    """Try to get JW Player sources after a tab click"""
    try:
        jw_playlist = driver.execute_script("""
            if (typeof jwplayer === 'function') {
                try {
                    var player = jwplayer();
                    if (player && player.getPlaylist) {
                        return JSON.stringify(player.getPlaylist());
                    }
                } catch(e) {}
            }
            return null;
        """)
        if jw_playlist and jw_playlist not in js_sources:
            js_sources.append(jw_playlist)
    except:
        pass


def is_stream_url(url):
    """Check if URL looks like a stream"""
    stream_indicators = ['.m3u8', '.mpd', '.ts', '.flv', 'rtmp://', '/live/', '/stream/', '/hls/']
    return any(indicator in url.lower() for indicator in stream_indicators)


def detect_stream_type(url):
    """Detect stream type from URL"""
    url_lower = url.lower()
    if '.m3u8' in url_lower:
        return 'HLS'
    elif '.mpd' in url_lower:
        return 'DASH'
    elif url_lower.startswith('rtmp://'):
        return 'RTMP'
    elif '.flv' in url_lower:
        return 'FLV'
    elif '.ts' in url_lower:
        return 'TS'
    elif '/live/' in url_lower or '/stream/' in url_lower:
        return 'Live Stream'
    return None


def find_urls_in_js(js_content, base_url):
    """Extract stream URLs from JavaScript content"""
    streams = []
    found_urls = set()
    
    # Patterns for stream URLs in JS
    patterns = [
        r'https?://[^\s\'"<>]+\.m3u8[^\s\'"<>]*',
        r'https?://[^\s\'"<>]+\.mpd[^\s\'"<>]*',
        r'rtmp://[^\s\'"<>]+',
        r'https?://[^\s\'"<>]*(?:live|stream|hls)[^\s\'"<>]*',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for url in matches:
            url = clean_url(url)
            if url and url not in found_urls:
                stream_type = detect_stream_type(url)
                if stream_type:
                    found_urls.add(url)
                    streams.append({
                        'url': url,
                        'type': stream_type,
                        'source': 'js_parse'
                    })
    
    return streams


def find_stream_urls(html_content, base_url, page_url):
    """
    Extract all video stream URLs from HTML content
    """
    streams = []
    found_urls = set()
    
    # Pattern definitions for different stream types
    patterns = {
        'hls': {
            'pattern': r'https?://[^\s\'"<>]+\.m3u8[^\s\'"<>]*',
            'type': 'HLS',
            'extension': '.m3u8'
        },
        'dash': {
            'pattern': r'https?://[^\s\'"<>]+\.mpd[^\s\'"<>]*',
            'type': 'DASH',
            'extension': '.mpd'
        },
        'rtmp': {
            'pattern': r'rtmp://[^\s\'"<>]+',
            'type': 'RTMP',
            'extension': ''
        },
        'flv': {
            'pattern': r'https?://[^\s\'"<>]+\.flv[^\s\'"<>]*',
            'type': 'FLV',
            'extension': '.flv'
        },
        'mp4_stream': {
            'pattern': r'https?://[^\s\'"<>]*(?:live|stream|video)[^\s\'"<>]*\.mp4[^\s\'"<>]*',
            'type': 'MP4 Stream',
            'extension': '.mp4'
        },
        'ts': {
            'pattern': r'https?://[^\s\'"<>]+\.ts[^\s\'"<>]*',
            'type': 'TS',
            'extension': '.ts'
        }
    }
    
    # Search for each pattern type
    for stream_type, config in patterns.items():
        matches = re.findall(config['pattern'], html_content, re.IGNORECASE)
        for url in matches:
            # Clean up URL
            url = clean_url(url)
            if url and url not in found_urls:
                found_urls.add(url)
                streams.append({
                    'url': url,
                    'type': config['type'],
                    'source': 'regex_match'
                })
    
    # Look for video/source tags with src
    video_src_pattern = r'<(?:video|source|iframe)[^>]*\s+src=["\']([^"\']+)["\']'
    video_matches = re.findall(video_src_pattern, html_content, re.IGNORECASE)
    for src in video_matches:
        full_url = urljoin(page_url, src)
        if full_url not in found_urls:
            # Determine type
            stream_type = 'Video Source'
            if '.m3u8' in full_url:
                stream_type = 'HLS'
            elif '.mpd' in full_url:
                stream_type = 'DASH'
            elif '.mp4' in full_url:
                stream_type = 'MP4'
            
            found_urls.add(full_url)
            streams.append({
                'url': full_url,
                'type': stream_type,
                'source': 'video_tag'
            })
    
    # Look for common player configurations (JSON-like patterns)
    json_patterns = [
        r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
        r'"src"\s*:\s*"([^"]+\.m3u8[^"]*)"',
        r'"source"\s*:\s*"([^"]+\.m3u8[^"]*)"',
        r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',
        r"'file'\s*:\s*'([^']+\.m3u8[^']*)'",
        r"'src'\s*:\s*'([^']+\.m3u8[^']*)'",
        r'"hls"\s*:\s*"([^"]+)"',
        r'"hlsUrl"\s*:\s*"([^"]+)"',
        r'"streamUrl"\s*:\s*"([^"]+)"',
        r'"m3u8"\s*:\s*"([^"]+)"',
        r'"playlist"\s*:\s*"([^"]+\.m3u8[^"]*)"',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for url in matches:
            full_url = urljoin(page_url, url) if not url.startswith('http') else url
            full_url = clean_url(full_url)
            if full_url and full_url not in found_urls:
                found_urls.add(full_url)
                streams.append({
                    'url': full_url,
                    'type': 'HLS (from config)',
                    'source': 'player_config'
                })
    
    # Look for iframe embeds that might contain videos
    iframe_pattern = r'<iframe[^>]*\s+src=["\']([^"\']+)["\']'
    iframe_matches = re.findall(iframe_pattern, html_content, re.IGNORECASE)
    for src in iframe_matches:
        full_url = urljoin(page_url, src)
        # Filter for likely video embeds
        video_domains = ['youtube', 'vimeo', 'dailymotion', 'twitch', 'facebook', 'player', 'embed', 'live', 'stream']
        if any(domain in full_url.lower() for domain in video_domains):
            if full_url not in found_urls:
                found_urls.add(full_url)
                streams.append({
                    'url': full_url,
                    'type': 'Iframe Embed',
                    'source': 'iframe'
                })
    
    return streams


def clean_url(url):
    """Clean and validate URL"""
    if not url:
        return None
    
    # Remove trailing garbage
    url = re.sub(r'[\'"\s<>].*$', '', url)
    
    # Remove common JS artifacts
    url = url.replace('\\/', '/')
    url = url.replace('\\u002F', '/')
    url = re.sub(r'\\u[0-9a-fA-F]{4}', '', url)
    
    # Remove trailing punctuation
    url = url.rstrip('.,;:')
    
    # Basic validation
    if not url.startswith(('http://', 'https://', 'rtmp://')):
        return None
    
    return url


def check_stream_status(url):
    """
    Check if a stream URL is accessible/alive
    Returns True if stream appears to be online
    Enhanced: More permissive checks with proper headers for livestream servers
    """
    try:
        # Extract domain for Referer header
        parsed = urlparse(url)
        referer = f"{parsed.scheme}://{parsed.netloc}/"
        origin = f"{parsed.scheme}://{parsed.netloc}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': origin,
            'Referer': referer,
            'Connection': 'keep-alive',
        }
        
        # Skip iframes - can't check directly
        if 'youtube' in url or 'vimeo' in url or 'twitch' in url:
            return True  # Assume major platforms are online
        
        # For HLS, try to fetch the playlist
        if '.m3u8' in url:
            # First try with Referer header
            response = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
            
            # Accept any 2xx status code
            if response.status_code >= 200 and response.status_code < 300:
                content = response.text.lower()
                # Valid m3u8 content indicators
                if '#extm3u' in content or '#ext-x-' in content or '.ts' in content or '.m3u8' in content:
                    return True
                # Some servers return minimal content, still consider online if 200
                if response.status_code == 200 and len(content) > 10:
                    return True
            
            # Status 302/301/307 = redirect, likely valid but need different access
            if response.status_code in [301, 302, 307, 308]:
                return True  # Redirect means server is responding
            
            # Try without Referer as fallback
            simple_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            try:
                response2 = requests.get(url, headers=simple_headers, timeout=10, verify=False, allow_redirects=True)
                if response2.status_code >= 200 and response2.status_code < 300:
                    return True
                if response2.status_code in [301, 302, 307, 308]:
                    return True
            except:
                pass
            
            # 403 Forbidden often means stream is protected but server is UP
            # We'll return "Unknown" status differently
            if response.status_code == 403:
                return True  # Server responds, just needs proper access
            
            return False
        
        # For RTMP, we can't easily check but assume valid format means it might be online
        if url.startswith('rtmp://'):
            return True  # Can't check RTMP directly
        
        # For other types, just check if accessible
        response = requests.head(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        return response.status_code in [200, 206, 302, 301, 307, 308, 403]
        
    except requests.exceptions.Timeout:
        # Timeout doesn't mean offline, server might be slow or need different access
        return True  # Return as potentially online
    except requests.exceptions.ConnectionError:
        return False  # Connection refused = truly offline
    except Exception as e:
        # Other errors - might still be accessible
        return False


@csrf_exempt
def check_single_stream(request):
    """
    API to check if a single stream URL is online
    POST: { "url": "https://example.com/stream.m3u8" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
        
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)
        
        status = check_stream_status(url)
        stream_type = detect_stream_type(url) or 'Unknown'
        
        return JsonResponse({
            'success': True,
            'url': url,
            'type': stream_type,
            'status': status,
            'status_text': 'Online' if status else 'Offline/Unreachable'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
