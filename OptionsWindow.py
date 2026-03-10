import sys
from tkinter import filedialog
import customtkinter as ctk
import tkinter as tk
import dotenv
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
from ResizeImageButton import *
import keyboard
from pathlib import Path


class OptionsWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("KiwiGrass")
        self.geometry("450x620")
        self.images_path = master.images_path
        self.hotkey_combo = master.hotkey_combo
        self.tesseract_path = master.tesseract_path
        self.listening = False
        self.speaking_speed = master.screenshot_state.speaking_speed

        self.grid_rowconfigure(6, weight=1)  # configure grid system
        self.grid_columnconfigure(4, weight=1)

        self.browse_button = ctk.CTkButton(master=self, text="Browse Files", command=self.browse_files)
        self.browse_button.grid(row=0, column=1, columnspan=4, pady=30, padx=15, sticky="ew")

        self.label_file_explorer = ctk.CTkLabel(master=self, text=f"Current path is: {self.tesseract_path}")
        self.label_file_explorer.grid(row=1, column=0, columnspan=5, padx=20, pady=20)

        self.hotkey_button = ctk.CTkButton(master=self, text="Change Hotkey", fg_color="#A88F14", hover_color="#6D5B0D",
                                           command=self.change_hotkey)
        self.hotkey_button.grid(row=2, column=1, columnspan=4, pady=30, padx=15, sticky="ew")

        self.label_hotkey = ctk.CTkLabel(master=self, text=f"The current hotkey(s) is: {self.hotkey_combo}")
        self.label_hotkey.grid(row=3, column=0, columnspan=5, padx=20, pady=20)

        self.sound_button = ResizeImageButton(image_path=os.path.join(self.images_path, "question_mark.png") , master=self, corner_radius=16,
                                              text="", height=70, width=80, fg_color="#F0F0F0", hover_color="#F0F0F0",
                                              command=self.read_options)
        self.sound_button.grid(row=4, column=1, columnspan=3, pady=30, padx=15)

        self.slider_label = ctk.CTkLabel(master=self, text=f"Speed: {self.speaking_speed}wpm")
        self.slider_label.grid(row=4, column=4, padx=30)

        self.speed_slider = ctk.CTkSlider(master=self, from_=1, to=300, number_of_steps=30, command=self.slider_event)
        self.speed_slider.grid(row=5, column=2, columnspan=4, pady=30, padx=15, sticky="we")
        self.speed_slider.set(self.speaking_speed)



        self.save_button = ctk.CTkButton(master=self, text="Save Changes",fg_color="#1DAA21", hover_color="#1DAA21",
                                         command=self.save_changes)
        self.save_button.grid(row=6, column=1, columnspan=4, pady=30, padx=15, sticky="ew")

        self.after(1, lambda: self.focus_force())

    def slider_event(self, value):
        self.speaking_speed = int(value)
        self.slider_label.configure(text=f"Speed: {self.speaking_speed}wpm    ")

    def read_options(self):
        text=("This is the options menu. From top to bottom this is what is listed:"
              "1. The Blue Browse Files button. It is necessary to maintain a file path to your tesseract installation."
              "Make sure this path leads to the tesseract exe or the text to speech will no longer function."
              "2. The current path of the tesseract installation."
              "3. The yellow change hotkey button. Clicking this will allow you to press buttons on your keyboard until you "
              "press escape. Whatever buttons pressed will be the new combination of hotkeys to take screenshots."
              "4. The current hotkey combination to take screenshots."
              "5. The button to play this along with the current speed of the words spoken in text to speech"
              "6. The slider to adjust how many words per minute are spoken. It starts at 1 and goes to 300. 200 is "
              "the default unless changed. "
              "7. The green save changes button. This will take whatever changes are currently staged and confirms them.")

        self.master.screenshot_state.read_text(text=text, button=self.sound_button)
    def set_icon(self):
        self.iconbitmap = self.images_path + "kiwi.ico"

    def browse_files(self):
        """
        Browses for exe files to update the tesseract path as needed.
        :return: Nothing
        """
        filepath = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("Exe Files",
                                                          "*.exe*"),
                                                         ("all files",
                                                          "*.*")))

        # Change label contents
        if filepath is not None and filepath != "":
            self.label_file_explorer.configure(text="Current path is: " + filepath)
            self.tesseract_path = filepath
        self.after(1, lambda: self.focus_force())

    def change_hotkey(self):
        """
        Uses keyboard library to take keyboard events and formats them into a new hotkey string
        :return: Nothing
        """

        def listen_keyboard():
            try:
                if self.listening: #Close it.
                    self.listening = False
                    pass
                else:
                    self.listening = True
                    self.hotkey_button.configure(border_color="#EF000F", border_width=2)
                    recorded = keyboard.record(until='esc')
                    recorded = recorded[:-1]
                    formatted_recorded = ""
                    for item in enumerate(recorded): # Enumerate all recorded inputs except the last (That's the cancel)
                        formatted_event_text = str(item[1]) #Format our event into string
                        print(formatted_event_text)
                        if "up" not in formatted_event_text: # We only want down stroke
                            if item[0] != 0:
                                formatted_recorded += "+" # Add the plus sign for our second and onwards
                            start_index = formatted_event_text.find('(') + 1 #
                            end_index = formatted_event_text.find(' ')
                            formatted_recorded += formatted_event_text[start_index:end_index] # Use our indexes to get our str
                    print(formatted_recorded)
                    self.hotkey_combo = formatted_recorded

                    if self.hotkey_combo != "": #Make sure we don't save a blank set
                        self.label_hotkey.configure(text="Current path is: " + formatted_recorded)

                    self.hotkey_button.configure(border_color="#EF000F", border_width=0)
                    self.listening = False
            except Exception as e:
                sys.exit(f"Error: {e}")

        threading.Thread(target=listen_keyboard).start()


    def save_changes(self):
        """
        Updates current hotkeys and etc to reflect the changes made in the settings. Rewrites the dotenv file too.
        :return: None
        """
        dotenv_path = Path('./settings.env')

        slider_speaking_speed = int(self.speed_slider.get())

        print(f"{self.tesseract_path} <- Tesseract path\n"
              f"{self.hotkey_combo} <- Hotkeys\n"
              f"{slider_speaking_speed} <- Speaking speed")

        # The ifs and such check to see if there is anything for each. We don't want to update null

        if self.tesseract_path != "":
            dotenv.set_key(dotenv_path, "TESSERACT_PATH", self.tesseract_path)
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        if self.hotkey_combo != "":
            dotenv.set_key(dotenv_path, "HOTKEY_COMBO", self.hotkey_combo)
            keyboard.remove_all_hotkeys()
            keyboard.add_hotkey(self.hotkey_combo, self.master.screenshot_state.overwrite_mouse_position)
            self.master.hotkey_combo = self.hotkey_combo

        if slider_speaking_speed is not None:
            dotenv.set_key(dotenv_path, "SPEAKING_SPEED", str(slider_speaking_speed))
            self.master.screenshot_state.speaking_speed = slider_speaking_speed

        self.master.screenshot_state.read_text(text="Settings updated.")
        tk.messagebox.showinfo(message="Settings updated.")
        self.after(1, lambda: self.focus_force())
