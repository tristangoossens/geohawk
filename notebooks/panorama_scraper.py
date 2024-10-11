import io
import json
import random
import time
import csv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class ImageScrapeService:
    @property
    def driver(self):
        return self._driver

    def __del__(self):
        self._driver.quit()

    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={user_agent}')

        # Open the website
        self._driver = webdriver.Chrome(options=self.chrome_options)
        self._driver.get("https://randomstreetview.com/us")

        # Wait for the page to load
        time.sleep(1)

        # Close any cookie popups
        self._close_cookie_popup()

    def _get_geolocation_data(self, address):
        """Private function to get geolocation data from the page."""
        locs = self._driver.execute_script("return randomLocations.us")
        locs = json.dumps(locs)
        locs = json.loads(locs)

        for location in locs:
            if location["formatted_address"] == address:
                return location
        return None

    def _close_cookie_popup(self):
        """Private function to close any cookie popups on the page if they are present."""
        try:
            self._driver.find_element(by=By.CLASS_NAME, value="fc-button")
            self._driver.find_element(by=By.CLASS_NAME, value="fc-button").click()
        except:
            print("Cookie popup 1 not present")

        try:
            self._driver.find_element(by=By.ID, value="cmpwrapper")
            shadow_elem = self._driver.execute_script('return arguments[0].shadowRoot', self._driver.find_element(by=By.ID, value="cmpwrapper"))
            shadow_elem.find_element(by=By.CLASS_NAME, value="cmpboxbtnyes").click()
        except:
            print("Cookie popup 2 not present")

    def _take_screenshot(self):
        """Private function to take a screenshot and crop it to 640x640."""
        screenshot = self._driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        # Crop the center of the screenshot to 640x640
        left = (1920 - 640) / 2
        top = (1080 - 940) / 2
        right = (1920 + 640) / 2
        bottom = (1080 + 340) / 2
        image = image.crop((left, top, right, bottom))
        return image

    def _extract_image_data(self):
        """Private function to extract image data including latitude and longitude."""
        address = self._driver.find_element(by="id", value="address").text

        # Get the geolocation data
        location = self._get_geolocation_data(address)
        if location is None:
            return None, None

        latitude = location.get("lat")
        longitude = location.get("lng")

        return latitude, longitude

    def _rotate_view(self, hold_time=0.6):
        """Private function to rotate the Street View image by holding the right arrow key."""
        actions = ActionChains(self._driver)

        # Press and hold the right arrow key
        actions.key_down(Keys.ARROW_RIGHT).perform()  # Hold down the key

        # Wait for the specified hold time
        time.sleep(hold_time)

        # Release the right arrow key
        actions.key_up(Keys.ARROW_RIGHT).perform()  # Release the key

    def _next_image(self):
        # Click on the next button
        self._driver.find_element(by="id", value="next").click()

        # Click into focus to enable keyboard input
        self._driver.find_element(By.TAG_NAME, value="body").click()

        # Wait for the next image to load (sleep randomly between 1 and 2.5 seconds)
        time.sleep(1 + 2 * random.random())


    def get_panorama_image(self):
        """Public function to get a panorama Street View image and return (lat, lon, image)."""
        try:
            # Next image
            self._next_image()

            # Extract the latitude and longitude from the page
            latitude, longitude = self._extract_image_data()
            if latitude is None or longitude is None:
                return None, None, None

            # Capture 4 screenshots to create a panorama
            images = []
            for i in range(4):
                images.append(self._take_screenshot())
                if i < 3:  # Rotate only 3 times for 4 images
                    self._rotate_view()
                    time.sleep(0.4)

            # Stitch the images horizontally
            panorama = self._stitch_images(images)

            return float(latitude), float(longitude), panorama
        except Exception as e:
            print(f"Error: {e}")
            return None, None, None

    def _stitch_images(self, images):
        """Private function to stitch images horizontally."""
        total_width = sum(image.width for image in images)
        max_height = max(image.height for image in images)

        panorama = Image.new('RGB', (total_width, max_height))

        current_x = 0
        for image in images:
            panorama.paste(image, (current_x, 0))
            current_x += image.width

        return panorama

# Usage
service = ImageScrapeService()

for i in range(1000, 5000):
    # Renew the service every 50 images
    if i % 50 == 0:
        service = ImageScrapeService()

    latitude, longitude, panorama = service.get_panorama_image()
    if latitude is not None and longitude is not None and panorama is not None:
        filename = f"{i}.png"
        panorama.save(f"data/panorama_img/{filename}")
        with open('data/panorama_image_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([latitude, longitude, filename])
    else:
        print("Error getting panorama image")