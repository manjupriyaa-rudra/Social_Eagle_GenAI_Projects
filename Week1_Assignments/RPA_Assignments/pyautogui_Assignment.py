import os
import time
import pyautogui
import webbrowser
import pyperclip  # For handling copy-paste safely

# -----------------------------
# CONFIGURATION
# -----------------------------
FOLDER_PATH = r"G:\Social Eagle\Projects\playwright"  # meta files folder
META_FILENAME = "metadata_report.txt"
FILE_PATH = os.path.join(FOLDER_PATH, META_FILENAME)
RECIPIENT_EMAIL = "manjupriyaar.learning@gmail.com"
EMAIL_SUBJECT = "Meta File Submission"
EMAIL_BODY = "Hi,\n\nPlease find attached the latest meta file.\n\nThanks."

# -----------------------------
# STEP 2: Open Gmail in browser
# -----------------------------
def open_gmail():
    webbrowser.open("https://mail.google.com/mail/u/0/#inbox?compose=new")
    time.sleep(10)  # wait for browser to open

# -----------------------------
# STEP 3: Use PyAutoGUI to fill email
# -----------------------------
def send_email(file_path):
    if not os.path.exists(file_path):
        print(f"Meta file not found: {file_path}")
        return
    
    # Copy recipient to clipboard
    pyperclip.copy(RECIPIENT_EMAIL)
    pyautogui.hotkey("ctrl", "v")  # Paste in "To" field
    time.sleep(1)
    pyautogui.press("tab")  # Move to subject
    
    pyperclip.copy(EMAIL_SUBJECT)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("tab")  # Move to body
    
    pyperclip.copy(EMAIL_BODY)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    
    # Attach file
    #pyautogui.hotkey("ctrl", "shift", "a")  # Gmail attachment shortcut (or click attach button manually)
    pyautogui.click(1325, 986)
    time.sleep(2)
    pyperclip.copy(file_path)
    pyautogui.hotkey("ctrl", "v")  # Paste file path
    pyautogui.press("enter")
    time.sleep(2)
    
    # Send email
    pyautogui.hotkey("ctrl", "enter")
    print(f"Email sent with attachment: {file_path}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    if os.path.exists(FILE_PATH):
        print(f"Using meta file: {FILE_PATH}")
        open_gmail()
        time.sleep(5)
        send_email(FILE_PATH)
    else:
        print("No meta file found in folder.")
