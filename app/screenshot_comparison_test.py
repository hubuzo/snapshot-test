from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageChops

class ScreenshotComparisonTest:
    def __init__(self, urls):
        self.urls = urls
        self.options = Options()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.screenshots_folder = self.get_screenshots_folder()

    def get_screenshots_folder(self):
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(os.getcwd(), 'screenshots', now)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def capture_screenshot(self, url):
        self.driver.get(url)
        # ウィンドウの高さをウェブサイトの高さに設定する
        self.driver.execute_script("return document.body.scrollHeight")
        body_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, body_height)
        # スクロールしながらスクリーンショットを撮る
        for i in range(0, body_height, 1080):
            self.driver.execute_script("window.scrollTo(0, " + str(i) + ");")
            file_path = os.path.join(self.screenshots_folder, url.replace('/', '_') + '_' + str(i) + '.png')
            self.driver.save_screenshot(file_path)

    def capture_screenshots(self):
        for url in self.urls:
            url = url.strip()
            self.capture_screenshot(url)

    def compare_images(self, current_image_path, previous_image_path, url):
        current_image = Image.open(current_image_path)
        previous_image = Image.open(previous_image_path)
        diff = ImageChops.difference(current_image, previous_image)
        if diff.getbbox() is not None:
            found_diff = True
            diff_file = os.path.join(self.screenshots_folder, 'diff', url + '.png')
            diff.save(diff_file)
            print(f'{url} has changed.')
        else:
            print(f'{url} comparison failed. No previous screenshot found.')

    def compare_screenshots(self):
        current_folder = self.screenshots_folder
        folders = sorted(os.listdir(os.path.join(os.getcwd(), 'screenshots')), reverse=True)
        if len(folders) <= 1:
            print('Comparison failed. No previous screenshots found.')
            return
        previous_folder = os.path.join(os.getcwd(), 'screenshots', folders[1])
        os.makedirs(os.path.join(current_folder, 'diff'), exist_ok=True)
        found_diff = False  # diffが見つかったかどうかのフラグ
        for url in self.urls:
            url = url.strip()
            current_files = [f for f in os.listdir(current_folder) if f.startswith(url.replace('/', '_'))]
            previous_files = [f for f in os.listdir(previous_folder) if f.startswith(url.replace('/', '_'))]
            for current_file in current_files:
                current_file_path = os.path.join(current_folder, current_file)
                previous_file_path = os.path.join(previous_folder, current_file)
                if os.path.exists(previous_file_path):
                    self.compare_images(current_file_path, previous_file_path, url)
                else:
                    print(f'{url} comparison failed. No previous screenshot found.')
        if not found_diff:
            print('All images are identical.')
