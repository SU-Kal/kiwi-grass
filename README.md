# kiwi-grass
Kiwigrass was made for the use case of playing video games with dyslexia or visual impairment. For many people it is a
struggle to play. This is intended to make it easier. This program will take two points, create a screenshot and then
use tesseract AI to grab the text and then read it out loud.

# Video Example:
https://youtu.be/D1FW54C6ooc 

## Requirements:
+ Python 3.12
+ Tesseract OCR (Installation link and info is: https://tesseract-ocr.github.io/tessdoc/Installation.html)

## How to use:
+ Install packages with command: `pip install -r requirements.txt`
+ Then run command: `python main.py`

There is an options menu you can access by clicking the gear. This is where you add the path to your tesseract.exe,
change hotkey configuration, and text to speech speed. Make sure you click the green save changes button at the bottom
to save any progress. 

## To compile with pyinstaller:
`pyinstaller --noconfirm --onedir --windowed --icon="./images/kiwi.ico" --add-data "./images;./images" --add-data "./settings.env;settings" --add-data "C:/<path_to_env>/Lib/site-packages/customtkinter;customtkinter/"  "./main.py"`