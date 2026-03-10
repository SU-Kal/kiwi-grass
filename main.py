import sys
import customtkinter as ctk
import dotenv
from PIL import ImageGrab
from functools import partial
from screenshot_state import *
from OptionsWindow import *
from ResizeImageButton import *
from dotenv import load_dotenv
import keyboard
import os
import imagesize as ims
from pathlib import Path

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)


BASE_DIR = os.path.dirname(__file__)

# If frozen application, we use settings/settings.env, else we use just file
env_path = os.path.join(os.path.join(BASE_DIR, "settings"), "settings.env") if getattr(sys, "frozen", False) else  (
    os.path.join(BASE_DIR, "settings.env"))

image_path = os.path.join(BASE_DIR, "images")

load_dotenv(dotenv_path=env_path)
tesseract_path = os.getenv('TESSERACT_PATH')
hotkey_combo = os.getenv("HOTKEY_COMBO")
speaking_speed = os.getenv("SPEAKING_SPEED")
from pytesseract import *
pytesseract.tesseract_cmd = tesseract_path


# Import screenshot state class and then assign hotkeys
screenshot_state = ScreenshotState(speaking_speed, image_path=image_path)

keyboard.add_hotkey(hotkey_combo, screenshot_state.overwrite_mouse_position)


class App(ctk.CTk):
    def __init__(self, screenshot_state, tesseract_path, hotkey_combo, image_path):
        super().__init__()
        self.scale = self.get_scaling()
        self.geometry("800x500")
        self.images_path = image_path
        self.iconbitmap(os.path.join(self.images_path, "kiwi.ico"), default=os.path.join(self.images_path, "kiwi.ico"))
        self.title("KiwiGrass")
        self.root_height = self.winfo_height()
        self.root_width = self.winfo_width()
        self.screenshot_state = screenshot_state
        self.tesseract_path = tesseract_path
        self.hotkey_combo = hotkey_combo
        self.toplevel_window = None

        self.screenshot_state.on_screenshot_taken = self.on_screenshot_taken

        self.label = ctk.CTkLabel(self, text="Waiting for screenshot...")
        self.label.place(relx=0.5, rely= 0.05, anchor="center", relwidth=0.2, relheight=0.298954)

        print(self.root_width / 2)

        self.textbox = ctk.CTkTextbox(master=self, scrollbar_button_color='#FFCC70', corner_radius=16, border_color="#FFFFFF",
                                      border_width=2, width=int(self.root_width / 2), height=int(self.root_height / 3.345))

        self.textbox.place(relx=0.5, rely= 0.83, anchor="center", relwidth=0.65, relheight=0.298954)

        self.image_label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.image_label.place(relx=0.5, rely=0.35, anchor="center", relwidth=0.85, relheight=0.55)

        self.sound_button = ResizeImageButton(image_path=os.path.join(self.images_path, "sound.png") ,master=self, corner_radius=16,
                                               text="", height=200, width=200, fg_color="#F0F0F0")
        self.sound_button.configure(command= lambda: self.click_sound_button(self.textbox.get("0.0", "end")))
        self.sound_button.place(relx = 0.1, rely = 0.82, anchor="center", relwidth=0.085, relheight=0.1 )

        self.screenshot_state.sound_button = self.sound_button

        self.settings_button = ResizeImageButton(image_path=os.path.join(self.images_path,  "gear.png"), master=self, corner_radius=16,
                                              text="", height=180, width=180, fg_color="#F0F0F0")
        self.settings_button.configure(command=lambda: self.click_settings_button())
        self.settings_button.place(relx=0.9, rely=0.1, anchor="center", relwidth=0.085, relheight=0.1)


    def get_scaling(self):
        scaling = self._get_window_scaling()
        return scaling

    def update_scaling(self):
        self.scale = self.get_scaling()

    def get_image_size(self, image_path):
        width, height = ims.get(image_path)
        dpi_scaling = self.get_scaling()
        self.image_label.update_idletasks()
        if width > self.image_label.winfo_width():
            print("Too wide")
            width = self.image_label.winfo_width() / dpi_scaling
        if height > self.image_label.winfo_height():
            print("Too tall")
            height = self.image_label.winfo_height() / dpi_scaling
        return width, height

    def click_sound_button(self, text):
        if text != "" and text is not None:
            self.screenshot_state.read_text(text=text)

    def on_screenshot_taken(self, image_path, text):
        self.label.configure(text="")
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        self.image_label.configure(image=ctk.CTkImage(dark_image=Image.open(image_path),
                                                                            size=(self.get_image_size(image_path))))

    def click_settings_button(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = OptionsWindow(self)  # create window if its None or destroyed
            # self.toplevel_window.iconbitmap(os.path.join(self.images_path, "kiwi.ico"), default=os.path.join(self.images_path, "kiwi.ico"))
        else:
            self.toplevel_window.focus()  # if window exists focus it
            # self.toplevel_window.iconbitmap(os.path.join(self.images_path, "kiwi.ico") , default=os.path.join(self.images_path, "kiwi.ico"))


app = App(screenshot_state, tesseract_path, hotkey_combo, image_path)
app.mainloop()