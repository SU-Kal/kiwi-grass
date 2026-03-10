import customtkinter as ctk
from PIL import ImageGrab
from functools import partial
from screenshot_state import *
from OptionsWindow import *


class ResizeImageButton(ctk.CTkButton):
    def __init__(self, master, image_path, **kwargs):
        super().__init__(master, **kwargs)

        self.original_image = Image.open(image_path)
        self.bind("<Configure>", self._idle_check) # Our callback for on configure resize
        self.configure(image=ctk.CTkImage(dark_image=self.original_image))
        self.current_image = None

    def _idle_check(self, event):
        self.master.after_idle(self._resize, event)

    def _resize(self, event):
        try:
            dpi_scale = self.master.get_scaling()

            if event.width < 10 or event.height < 10:
                return

            resized = self.original_image.resize(
                (event.width, event.height), Image.BILINEAR
            )


            self.current_image = ctk.CTkImage(dark_image=resized, size=(round((self.winfo_width()*0.55)/dpi_scale), round((self.winfo_height()*0.85)/dpi_scale)))
            self.configure(image=self.current_image)

        except:
            print("Top level window error. Ignore if not main.")
