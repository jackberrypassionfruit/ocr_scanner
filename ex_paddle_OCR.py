import os

# os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "1"
# os.environ["FLAGS_enable_pir_api"] = (
#     "0"  # Disables new PIR backend, fixes the C++ crash on CPU
# )

import cv2
import pyperclip
import pyautogui
from paddleocr import PaddleOCR
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class ScannerWorker(QThread):
    status_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self._alive = True
        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device="cpu",
        )

    def run(self):
        camera = cv2.VideoCapture(0)
        # last_val = ""
        # last_scan = ""

        while self._alive:
            if self.running:
                ret, image = camera.read()
                if not ret:
                    self.status_updated.emit("Camera read failed")
                    QThread.msleep(500)
                    continue

                try:
                    results = self.ocr.predict(input=image)
                    words = []
                    for res in results:
                        # 3.x results are dicts, not objects
                        if isinstance(res, dict) and "rec_texts" in res:
                            for text, score in zip(res["rec_texts"], res["rec_scores"]):
                                if score > 0.5:
                                    words.append(text)

                    if words:
                        print(words)
                        next_val = words[-1]
                        self.status_updated.emit(f"Seen: {next_val}")
                        # if 1 == 1:  # next_val == last_val and next_val != last_scan:
                        pyperclip.copy(next_val)
                        pyautogui.hotkey("ctrl", "v")
                        pyautogui.hotkey("enter")
                        # last_scan = next_val
                        self.status_updated.emit(f"✓ Scanned: {next_val}")
                        # else:
                        #     last_val = next_val
                    else:
                        self.status_updated.emit("No text detected")

                except Exception as e:
                    self.status_updated.emit(f"OCR error: {e}")

                QThread.msleep(200)
            else:
                # last_val = ""
                QThread.msleep(100)

        camera.release()

    def set_running(self, state: bool):
        self.running = state

    def stop(self):
        self._alive = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Scanner")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(250)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_label = QLabel("Press On to start scanning")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.toggle_button = QPushButton("Off")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.on_toggle)
        layout.addWidget(self.toggle_button)

        self.worker = ScannerWorker()
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.start()

    def on_toggle(self, checked: bool):
        self.toggle_button.setText("On" if checked else "Off")
        self.worker.set_running(checked)

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
