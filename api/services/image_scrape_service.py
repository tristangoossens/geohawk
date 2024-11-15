import io
import json
import random
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class ImageScrapeService:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--window-size=1920,1080")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        self.chrome_options.add_argument(f'user-agent={user_agent}')

    def _get_geolocation_data(self, driver, address):
        """Private function to get geolocation data from the page."""
        locs = driver.execute_script("return randomLocations.us")
        locs = json.dumps(locs)
        locs = json.loads(locs)

        for location in locs:
            if location["formatted_address"] == address:
                return location
        return None

    def _take_screenshot(self, driver):
        """Private function to take a screenshot and crop it to 640x640."""
        screenshot = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        # Crop the center of the screenshot to 640x640
        left = (1920 - 640) / 2
        top = (1080 - 940) / 2
        right = (1920 + 640) / 2
        bottom = (1080 + 340) / 2
        image = image.crop((left, top, right, bottom))
        return image

    def _extract_image_data(self, driver):
        """Private function to extract image data including latitude and longitude."""
        address = driver.find_element(by="id", value="address").text

        # Get the geolocation data
        location = self._get_geolocation_data(driver, address)
        if location is None:
            return None, None

        latitude = location.get("lat")
        longitude = location.get("lng")

        return latitude, longitude

    def _cookie_popup_1_present(self, driver):
        """Private function to check if the first cookie popup is present."""
        try:
            driver.find_element(by=By.CLASS_NAME, value="fc-button")
            return True
        except:
            return False

    def _cookie_popup_2_present(self, driver):
        """Private function to check if the second cookie popup is present."""
        try:
            driver.find_element(by=By.ID, value="cmpwrapper")
            return True
        except:
            return False

    def get_random_image(self):
        """Public function to get a random Street View image and return (lat, lon, image)."""
        # Instantiate the Chrome driver here to ensure it opens and closes per request
        driver = webdriver.Chrome(options=self.chrome_options)

        try:
            driver.get("https://randomstreetview.com/us")

            # Wait for the page to load
            time.sleep(1)

            # Check and close any cookie popups
            if self._cookie_popup_1_present(driver):
                driver.find_element(by=By.CLASS_NAME, value="fc-button").click()
            if self._cookie_popup_2_present(driver):
                shadow_elem = driver.execute_script('return arguments[0].shadowRoot', driver.find_element(by=By.ID, value="cmpwrapper"))
                shadow_elem.find_element(by=By.CLASS_NAME, value="cmpboxbtnyes").click()

            latitude, longitude = self._extract_image_data(driver)
            if latitude is None or longitude is None:
                return None, None, None

            image = self._take_screenshot(driver)
            return float(latitude), float(longitude), image
        finally:
            driver.quit()  # Ensure the driver quits even if an error occurs