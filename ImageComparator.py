from PIL import Image, ImageChops
import os
import cv2
import imagehash
from datetime import datetime

"""
同一階層にoldフォルダ, newフォルダを作成する
その２つのフォルダを参照して同一のファイル名を取得し、差分を検証する
差分検出結果はdiff配下に実行時間のフォルダを作成して保存する。
OpenCVなので画像のサイズが同一の場合のみ検証できる。
"""
class ImageComparator:
    def __init__(self, old_dir, new_dir, diff_dir):
        self.old_dir = old_dir
        self.new_dir = new_dir
        self.diff_dir = diff_dir
        self.found_diff = False

    def compare_images(self, current_image_path, previous_image_path, file_name):
        current_image_hash = imagehash.average_hash(Image.open(current_image_path)) 
        previous_image_hath = imagehash.average_hash(Image.open(previous_image_path)) 
        current_image = cv2.imread(current_image_path,0)
        previous_image = cv2.imread(previous_image_path,0)
        if current_image.shape != previous_image.shape:
            print(f'{file_name} is not same shape with previous image.')
        elif current_image_hash != previous_image_hath:
            self.found_diff = True
            diff_file = cv2.absdiff(current_image, previous_image)
            now = datetime.now()
            date_time = now.strftime("%Y%m%d_%H%M%S")
            diff_dir_path = os.path.join(self.diff_dir, date_time)
            os.makedirs(diff_dir_path, exist_ok=True)
            diff_file_path = os.path.join(diff_dir_path, file_name)
            cv2.imwrite(diff_file_path, diff_file)
            print(f'{file_name} has changed.')
    
    def run(self):
        for file_name in os.listdir(self.new_dir):
            if file_name in os.listdir(self.old_dir):
                old_image_path = os.path.join(self.old_dir, file_name)
                new_image_path = os.path.join(self.new_dir, file_name)

                self.compare_images(new_image_path, old_image_path, file_name)
        
        if not self.found_diff:
            print('All images are identical.')
        
        print('end jobs')

if __name__ == '__main__':
    comparator = ImageComparator('old', 'new', 'diff')
    comparator.run()
