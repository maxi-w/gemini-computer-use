import pyautogui


class ComputerTool:
    def __init__(self) -> None:
        pass

    def take_screenshot(self):
        img = pyautogui.screenshot()
        return img

    def click(self, x, y):
        pyautogui.moveTo(x, y, 2)
        pyautogui.click(button="left")

    def open_spotlight(self, search: str):
        pyautogui.keyDown("command")
        pyautogui.press("space")
        pyautogui.keyUp("command")
        pyautogui.typewrite(search)
        pyautogui.press("enter")

    def typewrite(self, text: str):
        pyautogui.typewrite(text)

    def press_key(self, name: str):
        pyautogui.press(name)

    def hotkey(self, *keys):
        pyautogui.hotkey(*keys)

