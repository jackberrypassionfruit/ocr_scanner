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

ocr = PaddleOCR(lang="en", cls=False, debug=False)


extract_result = []


def extract_all_words(ocr_result):
    global extract_result
    for sublist in ocr_result:
        if isinstance(sublist, list):
            extract_all_words(sublist)
        elif isinstance(sublist, tuple):
            word, confidence = sublist
            extract_result.append({"word": word, "confidence": confidence})


def filter_extract_result(extract_result):
    # pattern = re.compile(r"^P6-\d{3}$")
    al_p6_nums = [
        item["word"]
        for item in extract_result  # if pattern.match(item["word"])
    ]
    print(al_p6_nums)
    if len(al_p6_nums) == 0:
        return "ERROR - No P6 numbers found, please try again"
    elif len(al_p6_nums) > 1:
        return "ERROR - Too many P6 numbers found, please try again"
    else:
        return al_p6_nums[0]


if TESTING:
    img_fullpath = sys.argv[1]
    image = cv2.imread(img_fullpath)

    for i in range(5):
        ocr_result = ocr.ocr(image)
        # print(ocr_result[0].keys())

        extract_result = []
        extract_all_words(ocr_result)
        result = [item["word"] for item in extract_result]
        print(f"\n{result=}")

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

            ocr_result = ocr.ocr(image)

            extract_result = []
            extract_all_words(ocr_result)
            result_test_list = [item["word"] for item in extract_result]
            print(f"\n{result_test_list=}")
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
            time.sleep(0.1)
            print()
    except Exception as e:
        print(f"Exception: {e}")
        camera.release()
