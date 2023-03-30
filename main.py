from app.ScreenshotComparisonTest import ScreenshotComparisonTest 

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
