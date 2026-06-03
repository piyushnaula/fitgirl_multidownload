import os, re, requests, threading, queue
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
from colorama import Fore, Style


class console:
    def __init__(self) -> None:
        self.colors = {"green": Fore.GREEN, "red": Fore.RED, "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE, "black": Fore.BLACK, "reset": Style.RESET_ALL, "lightblack": Fore.LIGHTBLACK_EX, "lightred": Fore.LIGHTRED_EX, "lightgreen": Fore.LIGHTGREEN_EX, "lightyellow": Fore.LIGHTYELLOW_EX, "lightblue": Fore.LIGHTBLUE_EX, "lightmagenta": Fore.LIGHTMAGENTA_EX, "lightcyan": Fore.LIGHTCYAN_EX, "lightwhite": Fore.LIGHTWHITE_EX}

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def log_write(self, msg):
        try:
            tqdm.write(msg)
        except Exception:
            print(msg)
    
    def success(self, message, obj):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightgreen']}SUCC {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightgreen']}{obj}{self.colors['white']} {self.colors['reset']}")

    def error(self, message, obj):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightred']}ERRR {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightred']}{obj}{self.colors['white']} {self.colors['reset']}")

    def done(self, message, obj):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightmagenta']}DONE {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightmagenta']}{obj}{self.colors['white']} {self.colors['reset']}")

    def warning(self, message, obj):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightyellow']}WARN {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightyellow']}{obj}{self.colors['white']} {self.colors['reset']}")

    def info(self, message, obj):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightblue']}INFO {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightblue']}{obj}{self.colors['white']} {self.colors['reset']}")

    def custom(self, message, obj, color):
        self.log_write(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors[color.upper()]}{color.upper()} {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors[color.upper()]}{obj}{self.colors['white']} {self.colors['reset']}")

    def input(self, message):
        return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT   {self.colors['lightblack']}• {self.colors['white']}{message}{self.colors['reset']}")

log = console()
log.clear()

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'referer': 'https://fitgirl-repacks.site/',
    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

def download_file(download_url, output_path, headers=None, position=None):
    current_url = download_url
    max_redirects = 5
    redirect_count = 0
    
    while redirect_count < max_redirects:
        response = requests.get(current_url, stream=True, headers=headers)
        if response.status_code != 200:
            log.error(f"Failed To Fetch Download URL", response.status_code)
            return False
            
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            # Parse HTML and find redirect
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for downloadBtn first
            redirect_url = None
            btn = soup.find(id='downloadBtn')
            if btn and btn.get('data-url'):
                redirect_url = btn.get('data-url')
            
            # Look for redirect in meta refresh
            if not redirect_url:
                meta_refresh = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'})
                if meta_refresh and meta_refresh.get('content'):
                    content = meta_refresh.get('content')
                    parts = content.split('url=')
                    if len(parts) > 1:
                        redirect_url = parts[1].strip()
            
            # If not in meta, look in script tags
            if not redirect_url:
                scripts = soup.find_all('script')
                for script in scripts:
                    if not script.text:
                        continue
                    # Search window.location/replace
                    match = re.search(r'(?:window\.)?location(?:\.href)?\s*=\s*["\'](https?://[^\s"\']+)["\']', script.text)
                    if match:
                        redirect_url = match.group(1)
                        break
                    match = re.search(r'location\.replace\(\s*["\'](https?://[^\s"\']+)["\']\s*\)', script.text)
                    if match:
                        redirect_url = match.group(1)
                        break
                    # Search variables
                    match = re.search(r'(?:downloadUrl|fileUrl|download_url|url)\s*=\s*["\'](https?://[^\s"\']+)["\']', script.text)
                    if match:
                        redirect_url = match.group(1)
                        break
                    # General search for cfd/download URLs
                    match = re.search(r'["\'](https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}/download/[^\s"\']+)["\']', script.text)
                    if match:
                        redirect_url = match.group(1)
                        break
            
            if redirect_url:
                # Add headers for the redirect (like referer)
                log.info("Redirecting to real file source", f"{redirect_url[:70]}...")
                import time
                log.info("Simulating progress preparation", "5s")
                time.sleep(5)
                current_url = redirect_url
                redirect_count += 1
                continue
            else:
                log.error("Could not resolve final download link from HTML page", "")
                return False
        else:
            # It's the actual file! Download it.
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192

            with open(output_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                position=position,
                leave=True,
            ) as bar:
                for data in response.iter_content(block_size):
                    f.write(data)
                    bar.set_description(f"{log.colors['lightblack']}{log.timestamp()} » {log.colors['lightblue']}INFO {log.colors['lightblack']}• {log.colors['white']}Downloading -> {os.path.basename(output_path)[:55]} {log.colors['reset']}")
                    bar.update(len(data))

            log.success(f"Successfully Downloaded File", F"{output_path[:35]}...{output_path[55:]}")
            return True
            
    log.error("Too many HTML redirects", redirect_count)
    return False

file_lock = threading.Lock()

def remove_link(processed_link, input_file='input.txt'):
    with file_lock:
        with open(input_file, 'r') as file:
            links = file.readlines()
            
        with open(input_file, 'w') as file:
            for link in links:
                if link.strip() != processed_link:
                    file.write(link)

with open('input.txt', 'r') as file:
    links = [line.strip() for line in file if line.strip()]

if not links:
    log.warning("input.txt is empty", "add links and rerun")
    raise SystemExit(1)

# Try to determine game name from FuckingFast fragment or DataNodes path
game_name = "game_download"
for l in links:
    parsed = urlparse(l)
    if "fitgirl-repacks.site" in parsed.fragment:
        game_name = parsed.fragment.split("--")[0].strip("_")
        break
    elif "fitgirl-repacks.site" in parsed.path:
        basename = os.path.basename(parsed.path)
        game_name = basename.split("--")[0].strip("_")
        break

default_folder = os.path.join("downloads", game_name)
downloads_folder = log.input(f"Enter download folder path (press Enter for default '{default_folder}'): ").strip()
if not downloads_folder:
    downloads_folder = default_folder
os.makedirs(downloads_folder, exist_ok=True)
log.info("Download folder", downloads_folder)

def process_link(link_info):
    link, position = link_info
    log.info(f"Started Processing", f"{link[:30]}...{link[60:]}")
    try:
        response = requests.get(link, headers=headers)
    except Exception as e:
        log.error("Failed to connect to page", str(e))
        return

    if response.status_code != 200:
        log.error(f"Failed To Fetch Page", response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    parsed_url = urlparse(link)
    
    if "datanodes.to" in parsed_url.netloc:
        file_name = os.path.basename(parsed_url.path)
        if not file_name:
            file_name = "default_file_name"
            
        countdown_tag = soup.find('download-countdown')
        if countdown_tag:
            code = countdown_tag.get('code', '')
            rand = countdown_tag.get('rand', '')
            referer = countdown_tag.get('referer', '')
            free_method = countdown_tag.get('free-method', '')
            premium_method = countdown_tag.get('premium-method', '')
            
            # Wait for countdown
            try:
                countdown_secs = int(countdown_tag.get(':countdown', '5'))
            except ValueError:
                countdown_secs = 5
                
            log.info(f"Waiting countdown for {file_name[:25]}", f"{countdown_secs}s")
            import time
            time.sleep(countdown_secs)
            
            data = {
                'op': 'download2',
                'id': code,
                'rand': rand,
                'referer': referer,
                'method_free': free_method,
                'method_premium': premium_method,
                'g_captch__a': '1'
            }
            post_headers = headers.copy()
            post_headers['referer'] = link
            post_headers['x-requested-with'] = 'XMLHttpRequest'
            
            try:
                post_response = requests.post(link, data=data, headers=post_headers)
                if post_response.status_code == 200:
                    res_json = post_response.json()
                    if res_json and 'url' in res_json:
                        download_url = unquote(res_json['url'])
                        log.info(f"Found Download Url for {file_name[:25]}", f"{download_url[:70]}...")
                        output_path = os.path.join(downloads_folder, file_name)
                        try:
                            download_file(download_url, output_path, headers=headers, position=position)
                            remove_link(link)
                        except Exception as e:
                            log.error(f"Failed To Download File", str(e))
                    else:
                        log.error("DataNodes response JSON missing url", res_json.get('error', 'Unknown error'))
                else:
                    log.error("Failed to fetch DataNodes download link", post_response.status_code)
            except Exception as e:
                log.error("Error occurred while getting DataNodes link", str(e))
        else:
            log.error("Download countdown element not found on page", response.status_code)
    else:
        # FuckingFast
        meta_title = soup.find('meta', attrs={'name': 'title'})
        file_name = meta_title['content'] if meta_title else "default_file_name"
        script_tags = soup.find_all('script')
        download_function = None
        for script in script_tags:
            if 'function download' in script.text:
                download_function = script.text
                break

        if download_function:
            match = re.search(r'window\.open\(["\'](https?://[^\s"\'\)]+)', download_function)
            if match:
                download_url = match.group(1)
                log.info(f"Found Download Url for {file_name[:25]}", f"{download_url[:70]}...")
                output_path = os.path.join(downloads_folder, file_name)
                try:
                    download_file(download_url, output_path, headers=headers, position=position)
                    remove_link(link)
                except Exception as e:
                    log.error(f"Failed To Download File", str(e))
            else:
                log.error("No Download Url Found", response.status_code)
        else:
            log.error("Download Function Not Found", response.status_code)

# Ask for concurrent downloads
try:
    max_workers_input = log.input("Enter number of concurrent downloads (default 3): ").strip()
    max_workers = int(max_workers_input) if max_workers_input else 3
except ValueError:
    max_workers = 3

# Create position queue for unique progress bar offsets
position_queue = queue.Queue()
for i in range(max_workers):
    position_queue.put(i)

def worker(link):
    position = position_queue.get()
    try:
        process_link((link, position))
    finally:
        position_queue.put(position)

log.info(f"Starting downloads in parallel", f"{max_workers} threads")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    executor.map(worker, links)
        
