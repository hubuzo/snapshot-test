from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageChops
import concurrent.futures

class ScreenshotComparisonTest:
    def __init__(self, urls):
        self.urls = urls
        self.options = Options()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.screenshots_folder = self.get_screenshots_folder()
        self.found_diff = False

    def get_screenshots_folder(self):
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(os.getcwd(), 'screenshots', now)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def capture_screenshot(self, url):
        self.driver.get(url)
        self.driver.execute_script("return document.body.scrollHeight")
        body_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, body_height)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(0, body_height, 1080):
                executor.submit(self.capture_screenshot_part, url, i)

    def capture_screenshot_part(self, url, i):
        self.driver.execute_script("window.scrollTo(0, " + str(i) + ");")
        file_path = os.path.join(self.screenshots_folder, url.replace('/', '_') + '_' + str(i) + '.png')
        self.driver.save_screenshot(file_path)

    def capture_screenshots(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for url in self.urls:
                url = url.strip()
                executor.submit(self.capture_screenshot, url)

    def compare_images(self, current_image_path, previous_image_path, url):
        current_image = Image.open(current_image_path)
        previous_image = Image.open(previous_image_path)
        diff = ImageChops.difference(current_image, previous_image)
        if diff.getbbox() is not None:
            self.found_diff = True
            diff_file = os.path.join(self.screenshots_folder, 'diff', url + '.png')
            diff.save(diff_file)
            print(f'{url} has changed.')

    def compare_screenshots(self):
        current_folder = self.screenshots_folder
        folders = sorted(os.listdir(os.path.join(os.getcwd(), 'screenshots')), reverse=True)
        if len(folders) <= 1:
            print('Comparison failed. No previous screenshots found.')
            return
        previous_folder = os.path.join(os.getcwd(), 'screenshots', folders[1])
        os.makedirs(os.path.join(current_folder, 'diff'), exist_ok=True)
        for url in self.urls:
            url = url.strip()
            current_files = [f for f in os.listdir(current_folder) if f.startswith(url.replace('/', '_'))]
            previous_files = [f for f in os.listdir(previous_folder) if f.startswith(url.replace('/', '_'))]
            for current_file in current_files:
                current_file_path = os.path.join(current_folder, current_file)
                previous_file_path = os.path.join(previous_folder, current_file)
                self.compare_images(current_file_path, previous_file_path, url)
        if not self.found_diff:
            print('All images are identical.')
        else:
            print('end jobs')

