from dotenv import load_dotenv
import openai
import os
import platform
import pwd
import subprocess
import tempfile
import tkinter as tk


# Globals
code_prompt = """
You will be given some PC information, as well as a request and instructions/psuedo code to perform some computer action.
From this request and instructions derive some Python 3 code. Your job is to complete this task using the PC information provided
and general good programming skills. Only respond in code. Do not respond with any other text. Make sure to use correct spacing for
python, use 4 per indent. Use os.path.join() function for directories. Write only valid Python code that will run with no errors or
exceptions in a new environment. Never use back slashes, only use forward slashes. Pay close attention to any directory you specify,
it must have correct syntax. Do not forget to use "import [LIBRARY NAME]". You must import all libraries being used. The resulting code
must accomplish the request in its entirety. Do not include any comments in your code.
Example Valid Directories for Windows: "C:/Users/4manm/Desktop", "Minecraft"
Example Valid Directories for Linux: "/home/4manm/Desktop", "Minecraft"
"""
response_prompt = """
You will be given a request to do some computer task. From this request derive some sarcastic response. Use wit and poke fun at the
question. Act like the question is dumb. But ultimately you must explain that you will attempt to complete the task, but act hesitant.
Your response should be no more than 2 sentences in length.
"""

# Set the OpenAI API key to the environment variable, bail if it doesn't exist
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    print("OpenAI API Key not found in environment variables")
    exit()
else:
    print("API Key:", api_key)
    openai.api_key = api_key


def remove_non_utf8(text):
    return text.encode("utf-8", errors="ignore").decode("utf-8")

def perform_action(code):
    temp_dir = tempfile.gettempdir()
    with open(os.path.join(temp_dir, "ai_overlord.py"), "w") as file:
        # Write the contents to the file
        file.write(code)
        # Close the file
        file.close()

    # Run the Python file using the subprocess module
    subprocess.run(["python", os.path.join(temp_dir, "ai_overlord.py")])


def get_pc_info():
    # Get system and machine details
    system_info = platform.uname()
    system = system_info.system
    machine = system_info.machine

    # Get processor details
    processor = platform.processor()

    # Get Python version
    python_version = platform.python_version()

    # Get current user
    user = pwd.getpwuid(os.getuid()).pw_name

    # Get the path to the desktop directory
    desktop_dir = os.path.expanduser("~/Desktop")

    response_string = f"Computer Information:\n"
    response_string += f"System Info: {system_info}\n"
    response_string += f"System: {system}\n"
    response_string += f"Machine: {machine}\n"
    response_string += f"Processor: {processor}\n"
    response_string += f"Python Version: {python_version}\n"
    response_string += f"User: {user}\n"
    response_string += f"Desktop Directory: {desktop_dir}\n"
    response_string.replace("\\", "/")
    print(response_string)
    return response_string


def gpt_request(prompt):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.8,
      max_tokens=2024,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )

    response = response.choices[0].text
    return response


def begin_request(event):
  # Shift key is being held
  if event.state & 1:
    if text_area.get("1.0", tk.END) != "":
        # Add a newline
        text_area.insert(tk.END, "\n")
  else:
    # Get the contents of the text area
    text = text_area.get("1.0", tk.END)
    # Clear the text area
    text_area.delete("1.0", tk.END)

    response = gpt_request(response_prompt + "\n\n" + text + "\n\n")
    # Set the text of the display label
    display_label.configure(text=response)

    pc_info = get_pc_info()
    generated_code = gpt_request(code_prompt + "\n\n" + pc_info + "\n\n" + text + "\n\n")
    print("Generated Code:\n\n", generated_code, "\n\n")
    perform_action(remove_non_utf8(generated_code))



# Set color scheme
LIGHT_BG = "#353941"
DARK_BG = "#26282B"
OPTION_1 = "#5F85DB"
OPTION_2 = "#90B8F8"

# Create the main window
window = tk.Tk()
window.title("GPT3 Assistant")
window.configure(bg=LIGHT_BG)

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set window size and position
window.geometry("200x300")
window.minsize(400, 600)
window.maxsize(400, 600)
window.wm_geometry("200x300+{}+{}".format(int((screen_width - 400) / 2), int((screen_height - 600) / 2)))

# Create label with thick white letters in the center of the window
label = tk.Label(window, text="GPT3 Assistant", font=("Helvetica", 24, "bold"), fg="white", bg=LIGHT_BG)
label.pack(pady=(50, 0))

# Create a label to display the text above the text area
display_label = tk.Label(window, text="", font=("Helvetica", 12), fg=OPTION_2, bg=LIGHT_BG, wraplength=300)
display_label.pack(pady=(10, 0))

# Create text area at the bottom of the window
text_area = tk.Text(window, width=200, height=10, bg=DARK_BG, fg=OPTION_1, font=("Helvetica", 12), wrap=tk.WORD)
text_area.pack(side=tk.BOTTOM, fill=tk.X)

# Bind the <Return> event to the begin_request function
text_area.bind("<Return>", begin_request)

# Run the main loop
window.mainloop()
