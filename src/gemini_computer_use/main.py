import pyautogui
import re
import time

from google import genai
from .tools import ComputerTool


def main():
    client = genai.Client()
    computer = ComputerTool()

    #<spotlight>search</spotlight> Use this to use the MacOS Spotlight search for opening tools like browsers which is more reliable than clicking.
    #<spotlight>"name of the tool"</spotlight> Use this to use the MacOS Spotlight search for opening tools like browsers which is more reliable than clicking.

    prompt = """
    You are an assistant to control my computer. 
    Please help me to complete the goal I provide you.
    You don't have an option to ask questions as the user can only provide one initial goal. Try to compelete with the most reasonable option in case not sure.
    If there already is an application opened that would help with the task use it instead of opening another one.

    You can use a set of tools to complete the task:
    <screenshot> Use this to ask for a screenshot.
    <click>ymin, xmin, ymax, xmax</click> Use this and provide a bounding box of the target element in [ymin, xmin, ymax, xmax] format. Coordinates are normalized between 0 and 1000.
    <type>the text you want to type</type> Use this to provide a text you want to type on the keyboard.
    <key>a keyboard key</key> Use this to press a keyboard key.

    The follwoing are valid keyboard keys you could press:
    ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

    Only return one tool use instruction in each of your messages.
    """

    screen_width, screen_height = computer.take_screenshot().size
    click_width, click_height = pyautogui.size()

    print(screen_width, screen_height)
    print(click_width, click_height)

    goal = pyautogui.prompt(text='What do you want the Computer Agent to do?', title='Define the Task' , default='')
    assert goal is not None, "Goal was None"
    prompt += f"\nGoal: {goal}"

    messages = [prompt]
    for i in range(5):
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp', contents=messages
        )

        if "<screenshot>" in response.text:
            print(response.text)
            messages.append(computer.take_screenshot())
            continue

        if "<click>" in response.text:
            print(response.text)
            match = re.search(r'<click>(\d+),\s*(\d+),\s*(\d+),\s*(\d+)</click>', response.text)
            if match:
                #xmin, ymin, xmax, ymax = map(int, match.groups())
                ymin, xmin, ymax, xmax = map(int, match.groups())
                xmin = int((xmin / 1000) * screen_width)
                ymin = int((ymin / 1000) * screen_height)
                xmax = int((xmax / 1000) * screen_width)
                ymax = int((ymax / 1000) * screen_height)

                ymin = (ymin * (click_height / screen_height))
                xmin = (xmin * (click_width / screen_width))
                ymax = (ymax * (click_height / screen_height))
                xmax = (xmax * (click_width / screen_width))

                x = (xmin + xmax) // 2
                y = (ymin + ymax) // 2
                computer.click(x, y)
                messages.append(f"Successfully clicked {x}, {y}. The next Screenshot shows the state after the loading. Please verify whether the mouse hit the target element.")
                time.sleep(1)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when trying to parse click coordinates from {response.text}")
                break

        if "spotlight" in response.text:
            print(response.text)
            pattern = r"<spotlight>(.*?)</spotlight>"
            match = re.search(pattern, response.text)
            result = match.group(1) if match else None
            if result is not None:
                computer.open_spotlight(result)
                messages.append(f"Opened {result} with spotlight.")
                time.sleep(1)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when using spotlight with {response.text}")
                break

        if "type" in response.text:
            print(response.text)
            pattern = r"<type>(.*?)</type>"
            match = re.search(pattern, response.text)
            result = match.group(1) if match else None
            if result is not None:
                computer.typewrite(result)
                messages.append(f"Typed {result} on the keyboard.")
                time.sleep(0.5)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when trying to type {response.text}")
                break

        if "key" in response.text:
            print(response.text)
            pattern = r"<key>(.*?)</key>"
            match = re.search(pattern, response.text)
            result = match.group(1) if match else None
            if result is not None:
                computer.press_key(result)
                messages.append(f"Pressed {result} on the keyboard.")
                time.sleep(1)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when trying to press {response.text}")
                break

        print(response.text)
        break
