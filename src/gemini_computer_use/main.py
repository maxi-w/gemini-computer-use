import pyautogui
import re
import sys
import time
import PIL.PngImagePlugin

from google import genai
from .tools import ComputerTool


def main():
    assert len(sys.argv) > 1, "You need to provide an instruction for the agent with your start command."
    goal = sys.argv[1]
    print(goal)
    time.sleep(1)

    client = genai.Client()
    computer = ComputerTool()

    #<spotlight>search</spotlight> Use this to use the MacOS Spotlight search for opening tools like browsers which is more reliable than clicking.
    #<spotlight>"name of the tool"</spotlight> Use this to use the MacOS Spotlight search for opening tools like browsers which is more reliable than clicking.

    prompt = """
    You are an assistant to control my computer. 
    Please help me to complete the goal I provide you.
    You don't have an option to ask questions as the user can only provide one initial goal. Try to compelete with the most reasonable option in case not sure.
    If there already is an application opened that would help with the task use it instead of opening another one.

    You can use a set of tools to complete the task. Every message can contain only one such tool.
    If you want to type and press enter you should first only type and than press enter later after you got feedback on the typing.
    <screenshot> Use this to ask for a screenshot.
    <click>ymin, xmin, ymax, xmax</click> Use this and provide a bounding box of the target element in [ymin, xmin, ymax, xmax] format. Coordinates are normalized between 0 and 1000.
    <type>the text you want to type</type> Use this to provide a text you want to type on the keyboard. Only use it after you selected a textfield in which you can type.
    <key>a keyboard key</key> Use this to press a keyboard key.

    <hotkey>a hotkey</hotkey> Use this to press a hotkey.
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

    Use shortcuts whenever possible.
    In windows, to open taskbar items you can press win+number (1-9) hotkey.
    Add your reasoning also.
    Send <finish> if the goal is completed.
    """

    screen_width, screen_height = computer.take_screenshot().size
    click_width, click_height = pyautogui.size()

    print(screen_width, screen_height)
    print(click_width, click_height)
    prompt += f"\nGoal: {goal}"

    messages = [prompt]
    def is_goal_completed():
        messages = [f"Goal: {goal}. Send <finish> if the goal is completed. Else explain why it is not completed."]
        messages.append(computer.take_screenshot())
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp', contents=messages
        )
        response_text = response.text
        if "finish" in response_text:
            return True, "Goal is completed."
        return False, response_text

    last_response = None
    for i in range(50):
        print('Step', i+1)
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp', contents=messages
        )
        response_text = response.text
        if last_response == response_text:
            # to avoid loops
            response_text = '<finish>'
        last_response = response_text
        if "<screenshot>" in response_text:
            print(response_text)
            messages.append(computer.take_screenshot())
            continue

        if "<click>" in response_text:
            print(response_text)
            match = re.search(r'<click>(\d+),\s*(\d+),\s*(\d+),\s*(\d+)</click>', response_text)
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
                print(f"error when trying to parse click coordinates from {response_text}")
                break

        if "spotlight" in response_text:
            print(response_text)
            pattern = r"<spotlight>(.*?)</spotlight>"
            match = re.search(pattern, response_text)
            result = match.group(1) if match else None
            if result is not None:
                computer.open_spotlight(result)
                messages.append(f"Opened {result} with spotlight.")
                time.sleep(1)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when using spotlight with {response_text}")
                break

        if "type" in response_text:
            print(response_text)
            pattern = r"<type>(.*?)</type>"
            match = re.search(pattern, response_text)
            result = match.group(1) if match else None
            if result is not None:
                computer.typewrite(result)
                messages.append(f"Typed {result} on the keyboard.")
                time.sleep(0.5)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when trying to type {response_text}")
                break

        if "<key>" in response_text:
            print(response_text)
            pattern = r"<key>(.*?)</key>"
            match = re.search(pattern, response_text)
            result = match.group(1) if match else None
            if result is not None:
                computer.press_key(result)
                messages.append(f"Pressed {result} on the keyboard.")
                time.sleep(1)
                messages.append(computer.take_screenshot())
                continue
            else:
                print(f"error when trying to press {response_text}")
                break
        
        if "<hotkey>" in response_text:
            print(response_text)
            pattern = r"<hotkey>(.*?)</hotkey>"
            match = re.search(pattern, response_text)
            result = match.group(1) if match else None
            if result is not None:
                split_char = "+" if "+" in result else ","
                computer.hotkey(*result.split(split_char))
                messages.append(f"Pressed {result} on the keyboard.")
                continue

        print(response_text)
        if "<finish>" in response_text:
            status, message = is_goal_completed()
            if status:
                print(message)
                break
            else:
                messages.append(message)
                continue
