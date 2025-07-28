import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2

# import paddle
from paddleocr import PaddleOCR
import pyperclip
import pyautogui
import sys
import re
import time
from datetime import datetime

FILE_TITLE = "Test_Img"
TESTING = False

# gpu_available = paddle.device.is_compiled_with_cuda()
# print("GPU available:", gpu_available)

# ocr = PaddleOCR(lang="en")
# ocr = PaddleOCR(
#     use_textline_orientation=True, lang="en"
# )  # need to run only once to download and load model into memory
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang="en",
    # text_detection_model_dir=os.path.join(".", "models", "PP-OCRv5_server_det"),
    # text_recognition_model_dir=os.path.join(".", "models", "PP-OCRv5_server_rec"),
)

if TESTING:
    img_fullpath = sys.argv[1]
    image = cv2.imread(img_fullpath)

    for i in range(5):
        ocr_result = ocr.predict(image)
        # print(ocr_result[0].keys())
        result_test_list = ocr_result[0]["rec_texts"]
        print(result_test_list)

else:
    print("\nReady to Scan:")
    img_datetime = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
    img_file_name = f"{FILE_TITLE}_{img_datetime}.jpg"
    img_fullpath = os.path.join(".", "img", img_file_name)
    try:
        camera = cv2.VideoCapture(0)
        tries = 0
        scanned = False
        last_val = ""
        last_scan = ""
        while not scanned:
            tries += 1
            print(f"Try: #{tries}")
            _, image = camera.read()

            ocr_result = ocr.predict(image)
            result_test_list = ocr_result[0]["rec_texts"]
            print(result_test_list)
            if len(result_test_list) > 0:
                next_val = result_test_list[-1]
                print(f"{last_scan=}, {last_val=}, {next_val=}")
                if next_val == last_val and next_val != last_scan:
                    pyperclip.copy(result_test_list[-1])
                    pyautogui.hotkey("ctrl", "v")
                    pyautogui.hotkey("enter")
                    last_scan = next_val
                else:
                    last_val = next_val
                last_val = next_val
            print()
    except Exception as e:
        print(f"Exception: {e}")
        camera.release()
