from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageChops
import imagehash 
import concurrent.futures
import cv2

class ScreenshotComparisonTest:
    def __init__(self, urls):
        self.urls = urls
        self.options = Options()
        self.options.add_argument('--headless')
        self.screenshots_folder = self.get_screenshots_folder()
        self.found_diff = False

    def get_screenshots_folder(self):
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(os.getcwd(), 'screenshots', now)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def capture_screenshot(self, url):
        driver = webdriver.Chrome(options=self.options)
        driver.get(url)
        body_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, body_height)
        file_path = os.path.join(self.screenshots_folder, url.replace('/', '_') + '.png')
        driver.save_screenshot(file_path)

    def capture_screenshots(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for url in self.urls:
                url = url.strip()
                executor.submit(self.capture_screenshot, url)

    def compare_images(self, current_image_path, previous_image_path, url):
        current_image_hash = imagehash.average_hash(Image.open(current_image_path)) 
        previous_image_hath = imagehash.average_hash(Image.open(previous_image_path)) 
        current_image = cv2.imread(current_image_path,0)
        previous_image = cv2.imread(previous_image_path,0)
        if current_image.shape != previous_image.shape:
            print(f'{url} is not same shape with previous image.')
        elif current_image_hash != previous_image_hath:
            self.found_diff = True
            diff_file =  cv2.absdiff(current_image, previous_image)
            diff_file_name = os.path.join(self.screenshots_folder, 'diff', url.replace('/', '_') + '.png')
            cv2.imwrite(diff_file_name, diff_file)
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
                if not os.path.exists(previous_file_path):
                    print(f'{url} is not exists.')
                    continue
                self.compare_images(current_file_path, previous_file_path, url)
        if not self.found_diff:
            print('All images are identical.')
        else:
            print('end jobs')

if __name__ == '__main__':
    # URLリストを定義する
    urls = [
        'https://www.google.com/',
        'https://www.yahoo.co.jp/',
        'https://www.amazon.com/',
        'https://www.microsoft.com/',
    ]

    # ScreenshotComparisonTestクラスを初期化する
    test = ScreenshotComparisonTest(urls)

    # スクリーンショットを撮影する
    test.capture_screenshots()

    # スクリーンショットを比較する
    test.compare_screenshots()
