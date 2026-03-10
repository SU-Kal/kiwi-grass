import os
from PIL import ImageGrab, Image
from functools import partial
import pytesseract
import pyttsx3 as pytts
from pynput.mouse import Controller
import threading

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class ScreenshotState:
    def __init__(self, speaking_speed, image_path):
        self.mouse_position_1 = [0, 0]
        self.mouse_position_2 = [0, 0]
        self.first_position_active = False
        self.mouse_controller = Controller()
        self.image_name = "output.png"
        self.full_image_path = os.path.join(image_path, self.image_name)
        self.text = ""
        self.lang = "eng"
        self.on_screenshot_taken = None
        self.sound_button = None
        self.speaking_speed = int(speaking_speed)


    def take_snapshot(self):
        print(f"Taking snapshot of {self.mouse_position_1} and {self.mouse_position_2}")
        x1, y1, x2, y2 = self.mouse_position_1[0], self.mouse_position_1[1], self.mouse_position_2[0], self.mouse_position_2[1]
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            img.save(self.full_image_path)
            self.update_text()
            if self.on_screenshot_taken:
                self.on_screenshot_taken(self.full_image_path, self.text)
        except Exception as e:
            print("There was an error while taking this screenshot. Are you sure point 1 is further left than point 2?")
            print(e)
            raise


    def overwrite_mouse_position(self):

        mouse_position = self.mouse_controller.position

        if not self.first_position_active:
            self.mouse_position_1 = [mouse_position[0], mouse_position[1]]
            print(f"Updated first mouse position to {self.mouse_position_1}")
            self.first_position_active = True

        else:
            self.mouse_position_2 = [mouse_position[0], mouse_position[1]]
            print(f"Updated second mouse position to {self.mouse_position_2}")
            self.first_position_active = False
            self.take_snapshot()


        print(self.mouse_position_1, self.mouse_position_2)


    def update_text(self):
        img = Image.open(self.full_image_path).convert("L")
        self.text = " ".join(pytesseract.image_to_string(img, lang="eng").split())
        print(self.text)
        self.read_text()



    def read_text(self, text=None, button=None):

        def speak():
            if button:
                button.configure(border_color="#EF000F", border_width=2)
            else:
                self.sound_button.configure(border_color="#EF000F", border_width=2)
            if text is None: # If default, then we want to just read the class text. Else we want to use our TTS built in.

                if text != "" and text is not None:
                    self.screenshot_state.read_text(text=text)
                engine = pytts.init()
                engine.setProperty('rate', self.speaking_speed)
                engine.say(self.text)
                if engine._inLoop:
                    engine.endLoop()
                engine.runAndWait()
                engine.stop()

            elif text != "" and text is not None: # For when the parameter text is used and not blank.
                engine = pytts.init()
                engine.setProperty('rate', self.speaking_speed)
                engine.say(text)
                if engine._inLoop:
                    engine.endLoop()
                engine.runAndWait()
                engine.stop()

            else:
                pass
            if button:
                button.configure(border_color="#F0F0F0", border_width=0)
            else:
                self.sound_button.configure(border_color="#F0F0F0", border_width=0)

        # Worker doesn't work, but this does?
        threading.Thread(target=speak).start() # We run it in a thread to not interrupt later stuff.
