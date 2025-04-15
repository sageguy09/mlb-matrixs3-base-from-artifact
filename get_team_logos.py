import displayio
import terminalio
from adafruit_display_text import label
import os
import math
import time
try:
    import wifi
    import socketpool
    import ssl
    import adafruit_requests
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False
    print("Network libraries not available, using local files only")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available, using simplified image processing")

# Constants
LOGO_DIR = "/data"  # Writable directory for CircuitPython
LOGO_FILENAME = "ATL.bmp"  # Logo filename
LOGO_PATH = f"{LOGO_DIR}/{LOGO_FILENAME}"  # Full path to logo file
LOGO_READY = False  # Flag to track if logo is ready for display
GAMMA = 2.6
PASSTHROUGH = [
    (0, 0, 0),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 255),
    (0, 0, 255),
    (255, 0, 255),
    (255, 255, 255),
]

# Dictionary mapping team abbreviations to their logo file paths
TEAM_LOGOS = {
    "ATL": LOGO_PATH,
}

# Initialize session variable for requests
requests_session = None

def ensure_data_dir():
    """Make sure the data directory exists for saving files."""
    try:
        # List root directory contents
        contents = os.listdir('/')
        
        # Check if data directory exists
        if LOGO_DIR.strip('/') not in contents:
            # Create the directory if it doesn't exist
            os.mkdir(LOGO_DIR)
            print(f"Created directory {LOGO_DIR}")
        return True
    except Exception as e:
        print(f"Error ensuring data directory exists: {e}")
        return False

def initialize_network():
    """Initialize network connection if not already done."""
    global requests_session
    
    if not NETWORK_AVAILABLE:
        return False
        
    if requests_session is not None:
        return True
        
    try:
        # Check if WiFi is already connected (might have been initialized elsewhere)
        if not wifi.radio.connected:
            # Connect to WiFi if not already connected
            ssid = os.getenv("CIRCUITPY_WIFI_SSID")
            password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
            wifi.radio.connect(ssid, password)
            
        # Set up socketpool and requests
        pool = socketpool.SocketPool(wifi.radio)
        requests_session = adafruit_requests.Session(pool, ssl.create_default_context())
        return True
    except Exception as e:
        print(f"Error initializing network: {e}")
        return False

def process_image_pil(img_data, output_path):
    """
    Process the image data with PIL for optimal quality.
    Apply gamma correction and dithering.
    """
    try:
        # Save temporary PNG file
        temp_path = "/temp_logo.png"
        with open(temp_path, 'wb') as f:
            f.write(img_data)
            
        # Process with PIL
        img = Image.open(temp_path).convert('RGB')
        
        # Resize to 32x32 for the matrix
        img = img.resize((32, 32))
        
        # Apply dithering and gamma correction
        err_next_pixel = (0, 0, 0)
        err_next_row = [(0, 0, 0) for _ in range(img.size[0])]
        for row in range(img.size[1]):
            for column in range(img.size[0]):
                pixel = img.getpixel((column, row))
                want = (
                    math.pow(pixel[0] / 255.0, GAMMA) * 31.0,
                    math.pow(pixel[1] / 255.0, GAMMA) * 63.0,
                    math.pow(pixel[2] / 255.0, GAMMA) * 31.0,
                )
                if pixel in PASSTHROUGH:
                    got = (
                        pixel[0] >> 3,
                        pixel[1] >> 2,
                        pixel[2] >> 3,
                    )
                else:
                    got = (
                        min(max(int(err_next_pixel[0] * 0.5 +
                                err_next_row[column][0] * 0.25 +
                                want[0] + 0.5), 0), 31),
                        min(max(int(err_next_pixel[1] * 0.5 +
                                err_next_row[column][1] * 0.25 +
                                want[1] + 0.5), 0), 63),
                        min(max(int(err_next_pixel[2] * 0.5 +
                                err_next_row[column][2] * 0.25 +
                                want[2] + 0.5), 0), 31),
                    )
                err_next_pixel = (
                    want[0] - got[0],
                    want[1] - got[1],
                    want[2] - got[2],
                )
                err_next_row[column] = err_next_pixel
                rgb565 = (
                    (got[0] << 3) | (got[0] >> 2),
                    (got[1] << 2) | (got[1] >> 4),
                    (got[2] << 3) | (got[2] >> 2),
                )
                img.putpixel((column, row), rgb565)

        # Convert to 8-bit for smaller file size
        img = img.convert('P', palette=Image.ADAPTIVE)
        
        # Save as BMP
        img.save(output_path)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
            
        print(f"Logo processed with PIL and saved as {output_path}")
        return True
    except Exception as e:
        print(f"Error processing image with PIL: {e}")
        return False

def process_image(img_data, output_path):
    """
    Process the image data and save as BMP for matrix display.
    Tries to use PIL if available, otherwise falls back to raw data.
    """
    # Ensure the data directory exists
    ensure_data_dir()
    
    if PIL_AVAILABLE:
        return process_image_pil(img_data, output_path)
    
    # Fallback: just save the raw data
    try:
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print(f"Logo saved as {output_path} (raw data)")
        return True
    except Exception as e:
        print(f"Error saving logo: {e}")
        return False

def file_exists(filepath):
    """
    Check if a file exists in CircuitPython-compatible way.
    """
    try:
        # First ensure the directory exists
        if filepath.startswith(LOGO_DIR):
            ensure_data_dir()
            
        # Try to open the file
        with open(filepath, 'rb'):
            return True
    except OSError:
        # File doesn't exist or can't be opened
        return False

def fetch_braves_logo():
    """Fetch and process the Atlanta Braves logo."""
    global LOGO_READY
    
    # If the logo already exists, we don't need to fetch it
    if file_exists(LOGO_PATH):
        print(f"Logo already exists at {LOGO_PATH}")
        LOGO_READY = True
        return True
    
    if not NETWORK_AVAILABLE:
        print("Network not available, cannot fetch logo")
        return False
    
    # Initialize network connection
    if not initialize_network():
        print("Failed to initialize network")
        return False
    
    try:
        # ESPN API endpoint for Atlanta Braves
        url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/atl"
        print("Downloading Atlanta Braves logo...")
        
        response = requests_session.get(url)
        if response.status_code != 200:
            print("Failed to retrieve team data.")
            return False
        
        data = response.json()
        team_info = data.get('team', {})
        logos = team_info.get('logos', [])
        
        if not logos:
            print("No logos found for Atlanta Braves.")
            return False
            
        logo_url = logos[0].get('href', '')
        if not logo_url:
            print("No logo URL found for Atlanta Braves.")
            return False
        
        # Download the logo
        print(f"Downloading logo from {logo_url}...")
        response = requests_session.get(logo_url)
        
        if response.status_code == 200:
            if process_image(response.content, LOGO_PATH):
                LOGO_READY = True
                return True
        
        print("Failed to download logo.")
        return False
    
    except Exception as e:
        print(f"Error fetching logo: {e}")
        return False

def get_logo_tilegrid(team_code="ATL"):
    """
    Returns a displayio Group with the logo or text for the specified team code
    
    Args:
        team_code (str): Three-letter team code (currently only "ATL" is supported)
        
    Returns:
        displayio.Group: Group containing the team logo or text
    """
    # Create a group for the logo or text
    team_group = displayio.Group()
    
    # Only ATL is supported in this consolidated version
    if team_code != "ATL":
        team_code = "ATL"  # Force to ATL
    
    # Try to fetch logo if it doesn't exist yet
    if not LOGO_READY:
        fetch_braves_logo()
    
    # Wait for logo to be ready - add a timeout to prevent infinite waiting
    timeout = 10  # seconds
    start_time = time.monotonic()
    
    while not LOGO_READY and time.monotonic() - start_time < timeout:
        print("Waiting for logo to be ready...")
        time.sleep(0.5)
    
    try:
        # Try to load the bitmap
        if file_exists(LOGO_PATH):
            bitmap = displayio.OnDiskBitmap(LOGO_PATH)
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
            team_group.append(tile_grid)
        else:
            raise FileNotFoundError(f"Logo file not found at {LOGO_PATH}")
    except Exception as e:
        print(f"Error loading logo for {team_code}: {e}")
        # Create text as fallback
        text_label = label.Label(terminalio.FONT, text=team_code, color=0xFFFFFF)
        team_group.append(text_label)
    
    return team_group

# Initialize - try to fetch the Braves logo when module is imported
try:
    # Only try to fetch the logo if we can connect to the network
    if initialize_network():
        fetch_braves_logo()
except Exception as e:
    print(f"Could not prefetch logo: {e}")
