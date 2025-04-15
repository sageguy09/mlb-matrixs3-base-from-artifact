#!/usr/bin/env python3
# SPDX-License-IdentifierText: 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Script to download, resize, and convert MLB team logos for the
Braves LED Scoreboard project for Adafruit MatrixPortal S3.
Reads team setting from settings.toml and downloads
only that team's logo, properly sized for the display.
"""

import os
import math
import requests
from PIL import Image
import toml
import sys

# Constants for image processing
GAMMA = 2.6
MAX_WIDTH = 15  # Reduced from 24 to 15
MAX_HEIGHT = 15  # Reduced from 24 to 15

PASSTHROUGH = ((0, 0, 0),
               (255, 0, 0),
               (255, 255, 0),
               (0, 255, 0),
               (0, 255, 255),
               (0, 0, 255),
               (255, 0, 255),
               (255, 255, 255))

def process_image_pil(img_data, output_path):
    """
    Process the image data with PIL for optimal quality.
    Apply gamma correction and dithering.
    """
    try:
        # Save temporary PNG file
        temp_path = "temp_logo.png"
        with open(temp_path, 'wb') as f:
            f.write(img_data)
            
        # Process with PIL
        img = Image.open(temp_path).convert('RGB')
        
        # Calculate appropriate size - maintain aspect ratio with maximum dimensions
        width, height = img.size
        aspect_ratio = width / height
        
        if width > height:
            new_width = min(MAX_WIDTH, width)
            new_height = int(new_width / aspect_ratio)
            if new_height > MAX_HEIGHT:
                new_height = MAX_HEIGHT
                new_width = int(new_height * aspect_ratio)
        else:
            new_height = min(MAX_HEIGHT, height)
            new_width = int(new_height * aspect_ratio)
            if new_width > MAX_WIDTH:
                new_width = MAX_WIDTH
                new_height = int(new_width / aspect_ratio)
        
        # Resize with high-quality resampling
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Create a black background for padding
        padded_img = Image.new("RGB", (MAX_WIDTH, MAX_HEIGHT), (0, 0, 0))
        
        # Center the resized image on the background
        offset_x = (MAX_WIDTH - new_width) // 2
        offset_y = (MAX_HEIGHT - new_height) // 2
        padded_img.paste(img, (offset_x, offset_y))
        
        # Apply dithering and gamma correction
        dithered_img = apply_dithering(padded_img)
        
        # Save as BMP
        dithered_img.save(output_path, format="BMP")
        
        # Remove temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        print(f"Successfully processed and saved {output_path}")
        print(f"Final dimensions: {MAX_WIDTH}x{MAX_HEIGHT} pixels")
        return True
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def apply_dithering(img, output_8_bit=True, passthrough=PASSTHROUGH):
    """
    Apply gamma correction and error-diffusion dithering.
    Adapted from the original process() function.
    """
    width, height = img.size
    err_next_pixel = (0, 0, 0)
    err_next_row = [(0, 0, 0) for _ in range(width)]
    
    for row in range(height):
        for column in range(width):
            pixel = img.getpixel((column, row))
            want = (math.pow(pixel[0] / 255.0, GAMMA) * 31.0,
                    math.pow(pixel[1] / 255.0, GAMMA) * 63.0,
                    math.pow(pixel[2] / 255.0, GAMMA) * 31.0)
            
            if pixel in passthrough:
                got = (pixel[0] >> 3,
                       pixel[1] >> 2,
                       pixel[2] >> 3)
            else:
                got = (min(max(int(err_next_pixel[0] * 0.5 +
                                   err_next_row[column][0] * 0.25 +
                                   want[0] + 0.5), 0), 31),
                       min(max(int(err_next_pixel[1] * 0.5 +
                                   err_next_row[column][1] * 0.25 +
                                   want[1] + 0.5), 0), 63),
                       min(max(int(err_next_pixel[2] * 0.5 +
                                   err_next_row[column][2] * 0.25 +
                                   want[2] + 0.5), 0), 31))
                                   
            err_next_pixel = (want[0] - got[0],
                              want[1] - got[1],
                              want[2] - got[2])
            err_next_row[column] = err_next_pixel
            
            rgb565 = ((got[0] << 3) | (got[0] >> 2),
                      (got[1] << 2) | (got[1] >> 4),
                      (got[2] << 3) | (got[2] >> 2))
                      
            img.putpixel((column, row), rgb565)

    if output_8_bit:
        img = img.convert('P', palette=Image.ADAPTIVE)
        
    return img

def get_team_logo(team_abbr="ATL"):
    """Download logo for specified MLB team."""
    try:
        # First try direct team URL with abbreviation
        team_url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_abbr.lower()}"
        response = requests.get(team_url)
        
        # If team not found by abbreviation, search all teams
        if response.status_code != 200:
            print(f"Team {team_abbr} not found directly, searching all teams...")
            all_teams_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"
            response = requests.get(all_teams_url)
            data = response.json()
            
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            team_data = None
            
            for team in teams:
                if team['team']['abbreviation'].upper() == team_abbr.upper():
                    team_data = team['team']
                    break
                    
            if not team_data:
                print(f"Team {team_abbr} not found in MLB teams list.")
                return None
        else:
            team_data = response.json().get('team', {})
            
        # Get logo URL
        if not team_data or 'logos' not in team_data or not team_data['logos']:
            print(f"No logo found for team {team_abbr}.")
            return None
            
        logo_url = team_data['logos'][0]['href']
        print(f"Found logo for {team_abbr}: {logo_url}")
        
        # Download the logo
        img_response = requests.get(logo_url, stream=True)
        if img_response.status_code != 200:
            print(f"Failed to download logo: HTTP {img_response.status_code}")
            return None
            
        return img_response.content
        
    except Exception as e:
        print(f"Error getting team logo: {e}")
        return None

def main():
    """Main function to download and process team logo."""
    # Ensure the images directory exists
    os.makedirs("images", exist_ok=True)
    
    # Try to load team from settings.toml
    team_abbr = "ATL"  # Default to Braves
    try:
        settings = toml.load("settings.toml")
        team_abbr = settings.get("FAVORITE_TEAM", "ATL").upper()
        print(f"Using team from settings.toml: {team_abbr}")
    except Exception as e:
        print(f"Could not load settings.toml: {e}")
        print(f"Using default team: {team_abbr}")
    
    # Download the team logo
    logo_data = get_team_logo(team_abbr)
    if not logo_data:
        print("Failed to retrieve logo. Exiting.")
        sys.exit(1)
    
    # Process and save the logo
    output_path = f"images/{team_abbr}.bmp"
    if process_image_pil(logo_data, output_path):
        print(f"Logo for {team_abbr} has been successfully downloaded and processed!")
        print(f"Logo saved to: {os.path.abspath(output_path)}")
        print(f"Your code.py can load it using: displayio.OnDiskBitmap('/images/{team_abbr}.bmp')")
    else:
        print("Failed to process logo.")
        sys.exit(1)

if __name__ == "__main__":
    main()
