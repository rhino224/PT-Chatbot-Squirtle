import threading
import os
import subprocess
import sys
import textwrap
import time
import importlib

import keyboard
import google.generativeai as palm
import pickle
import json

# # Set the TCL_LIBRARY environment variable to the directory containing sv.tcl
# os.environ['TCL_LIBRARY'] = os.path.join(os.path.dirname(__file__), "theme", "sv_ttk")
from tkinter import *
from tkinter import ttk
import tkinter as tk
from ttkthemes import ThemedTk
import sv_ttk

# import customtkinter

restart_program_flag = False


# key_sequence = ""
# key_presses = 0  # Counter for the number of key presses without detection


class Chatbot:  ##################################################################

    def __init__(self, parent, my_text):
        super().__init__()
        self.parent = parent  # Store a reference to the parent ChatbotGUI instance
        self.response = None
        self.my_text = my_text

    # Implement Chat History Logic
    def get_conversation_history(self):
        conversation_history = self.parent.my_text.get("1.0", END)
        return conversation_history

    # Convert Conversation History to usable string type
    def full_conversation(self, user_input):
        try:
            conversation_history = self.get_conversation_history()

            # Convert the Conversation History list to a formatted string
            formatted_conversation_history = '\n'.join(conversation_history)

            # Concatenate user input and formatted conversation history
            our_full_conversation = formatted_conversation_history + f"\nUser: {user_input}\n"
            # self.my_text.insert(END, "ChatBot Full Convo: " + our_full_conversation + "\n\n") REMOVE IF NOT NECESSARY
            return our_full_conversation

        except Exception as e:
            return f"There was an error with Full Conversation: {e}"

    # Implement chatbot response logic
    def bot_response(self, user_input):
        print(f"User Inputer at top of Bot Response: " + user_input)
        try:
            full_conversation = self.full_conversation(user_input)
            if self.response is None:
                self.response = palm.chat(
                    model='models/chat-bison-001',
                    messages=full_conversation)
            else:
                self.response = self.response.reply(user_input)
                print(f"user input in bot_response" + user_input)
            return self.response  # Return the last response from the model
        except Exception as e:
            return f"There was an error with bot_response: {e}"


class ChatbotGUI:  ##################################################################

    def __init__(self, parent):
        super().__init__()
        self.api_key = None
        self.user_input = None
        self.my_text = None
        self.api_entry = None
        self.chat_entry = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.init_chatbot_gui()
        self.chatbot_instance = Chatbot(self, self.my_text)
        self.style = None

    def init_chatbot_gui(self):
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Configure row and column weights
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        # Create Text Frame
        text_frame = ttk.Frame(self.frame, padding=20)
        text_frame.grid(row=2, column=0, pady=5, padx=15, sticky="w")

        # Add Label for Chatbot Text Box
        text_box_label = ttk.Label(self.frame, justify=LEFT, anchor=W, padding=20, text="PT Chat Bot Discussion", style='header.TLabel')
        text_box_label.grid(row=1, column=0)

        # Add Text Widget To Get PaLM ChatBot Responses
        self.my_text = tk.Text(text_frame,
                               bg="#343638",  # Darker grey background color of textbox.
                               width=100,
                               height=30,
                               bd=1,  # boarder width, making it small.
                               fg="#d6d6d6",  # light grey color of the text.
                               relief="flat",  # gets rid of the white line around the textbox.
                               wrap=WORD,  # wraps whole words instead of partial words
                               selectbackground="#1f538d"  # Bluish color when selecting text.
                               )
        self.my_text.configure(font=("Helvetica", 12, "bold"))
        self.my_text.tag_configure('user', background='#5D97EC')
        self.my_text.tag_configure('chatbot', background='#818B99')
        self.my_text.grid(row=1, column=0)

        # Create Scrollbar for Text Widget
        text_scroll = ttk.Scrollbar(text_frame, command=self.my_text.yview)
        text_scroll.grid(row=1, column=1,
                         sticky='ns')  # sticky=ns makes the scrollbar go all the way up/down (north/south)

        # Add the scrollbar to the textbox
        self.my_text.configure(yscrollcommand=text_scroll.set)

        # Entry Widget to Type Stuff to ChatBot
        self.user_input = tk.StringVar()  # Declaring String Variable
        self.chat_entry = ttk.Entry(self.frame,
                                    width=101,
                                    textvariable=self.user_input)
        self.chat_entry.grid(row=3, column=0)

        # Bind the <Return> key press event to the entry widget
        self.chat_entry.bind("<Return>", self.speak)

        # Create Button Frame
        button_frame = ttk.Frame(self.frame, padding=10)
        button_frame.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        # Create Submit Button
        submit_button = ttk.Button(button_frame,
                                   text="Speak To ChatBot",
                                   command=self.speak,
                                   width=30,
                                   style='mystyle.TButton')
        submit_button.grid(row=0, column=0, padx=25, pady=10)

        # Create Clear Button
        clear_button = ttk.Button(button_frame,
                                  text="Clear Response",
                                  command=self.clear,
                                  width=20,
                                  style='mystyle.TButton')
        clear_button.grid(row=0, column=1, padx=35, pady=10)

        # Create API Button
        api_button = ttk.Button(button_frame,
                                text="Update API Key",
                                command=self.key,
                                width=20,
                                style='mystyle.TButton')
        api_button.grid(row=0, column=2, padx=25, pady=10)

        # Add API Key Frame
        api_frame = ttk.Frame(self.frame, borderwidth=1)
        api_frame.grid(row=5, column=0, padx=10, pady=40)

        # Initially Hide Frame
        api_frame.pack_forget()

        # Add API Entry Widget
        # Add API Entry Label
        api_label = ttk.Label(api_frame,
                              text="Enter Your API Key: ")
        api_label.grid(row=0, column=0, padx=10, pady=10)

        # Add API Entry Textbox
        self.api_key = tk.StringVar()  # Declaring String Variable
        self.api_entry = ttk.Entry(api_frame,
                                   width=50,
                                   textvariable=self.api_key,
                                   style='mystyle.TButton')
        self.api_entry.grid(row=0, column=1, padx=20, pady=15)

        # Add API Button
        api_save_button = ttk.Button(api_frame,
                                     text="Save Key",
                                     command=self.key_save)
        api_save_button.grid(row=0, column=2, padx=10)

    def speak(self, event=None):
        filename = "api_key"
        user_input = self.user_input.get()  # Get the value from the StringVar
        if user_input:
            try:
                if os.path.isfile(filename):
                    # Open the File
                    with open(filename, 'rb') as input_file:  # 'rb' allows us to just read the file name
                        # Load the data from the file into a variable
                        stuff = pickle.load(input_file)

                    # Query Chatbot
                    # Define our API Key to Chatbot
                    palm.configure(api_key=stuff)  # We put our API Key into 'stuff'

                    # Send user_input to 'Chatbot' Class and return 'response'
                    response = self.chatbot_instance.bot_response(user_input)

                    self.my_text.insert(END, "You: " + user_input + "\n\n", 'user')
                    self.my_text.insert(END, "ChatBot: " + response.last + "\n\n", 'chatbot')

                    # Clear Users Textbox
                    self.chat_entry.delete(0, END)

                else:
                    # Create the file
                    with open(filename,
                              'wb') as input_file:  # 'wb' allows us to write the file name and create it for us
                        pass
                    # Close the File
                    input_file.close()

                    self.my_text.insert(END,
                                        "\n\nYou Need An API Key To Talk With ChatBot. Get one here: "
                                        "\nhttps://developers.generativeai.google/guide/palm_api_overview")
            except Exception as e:
                error_message = f"There was an error with speak: {e}"
                self.my_text.insert(END, error_message + "\n\n")
                print(error_message)

        else:
            self.my_text.insert(END, "\n\nHey! You Forgot To Type Anything!")

    def clear(self):
        # Clear The Main Text Box
        self.my_text.delete(1.0, END)  # 1.0 is just the very start of Text Boxes

        # Clear The Query Entry Widget
        self.chat_entry.delete(0, END)  # 0 is just the very start of Widgets

    def key(self):
        # Define File Name
        filename = "api_key"
        try:
            if os.path.isfile(filename):
                # Open the file
                with open(filename, 'rb') as input_file:  # 'rb' allows us to just read the file name
                    # Load the data from the file into the variable
                    stuff = pickle.load(input_file)

                # Output Stuff to Our Entry Box
                self.api_key = stuff  # 'END' will insert it at the end of the box then ',' what we want to insert
                self.api_entry.config(show=self.api_key)
            else:
                # Create the file
                with open(filename, 'wb') as input_file:  # 'wb' allows us to write the file name and create it for us
                    pass

                # close the file
                input_file.close()
        except Exception as e:
            self.my_text.insert(END, f"\n\n There was an error \n\n{e}")

        # Re-Size App Smaller
        self.parent.winfo_toplevel().geometry("1200x1000")

    def key_save(self):
        # Define our filename
        filename = "api_key"

        try:
            # Open File
            with open(filename, 'wb') as output_file:
                # Actually add the data to the file
                pickle.dump(self.api_key.get(),
                            output_file)  # Grab key from the textbox then ',' dump it into the 'output_file' we just created

            # Delete Entry Box Text
            self.api_key.delete(0, END)

            # Hide API Frame
            self.api_frame.pack_forget()

            # Re-Size App Larger
            self.parent.winfo_toplevel().geometry("1200x800")

        except Exception as e:
            self.my_text.insert(END, f"\n\n There was an error \n\n{e}")

    def show(self):
        self.frame.pack(fill='both', expand=True)


class TextReplacementGUI:  ##################################################################
    def __init__(self, parent):
        super().__init__()
        self.key_input = None
        self.phrase_input = None
        self.key_entry = None
        self.phrase_entry = None
        self.my_display_text = None
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.init_text_replacement_gui()
        self.display_dict()

        self.json_filename = 'replacements.json'
        self.replacements_dict = {}  # Define Replacements Dictionary

        # Define a tag named "bold" for the "bold" style
        self.my_display_text.tag_configure("bold", font=("Helvetica", 11, "bold"))
        self.my_display_text.tag_configure("normal", font=("Helvetica", 11))

    def open_file(self):
        if not os.path.isfile('replacements.json'):
            with open('replacements.json', 'w') as json_file:
                json.dump({}, json_file)
        with open(self.json_filename, 'r') as open_file:
            return open_file

    def json_to_pythonDict(self):
        replacements = open_file(json_filename)
        print("This is JSON", type(replacements))

        print("\nNow convert from JSON to Python")

        # Convert string to Python dict
        self.replacements_dict = json.loads(replacements)
        print("Converted to Python", type(self.replacements_dict))
        print(self.replacements_dict)
        return self.replacements_dict

    # 'Write' the 'key' and 'replacement' to the JSON file
    def submit_key_replacement(self, event=None):
        key_input = self.key_input.get()
        phrase_input = self.phrase_input.get()
        if key_input and phrase_input:
            try:
                self.replacements_dict[key_input] = phrase_input

                # Update the displayed dictionary in the GUI
                self.update_displayed_dict()

                print("Key and Replacement Added.")
            except Exception as e:
                self.show_error_message(e)

        else:
            print("You Forgot to Type Something!")

    # Display data from JSON file onto Textbox with program startup
    def display_dict(self):
        json_filename = 'replacements.json'
        with open(json_filename, 'r') as open_file:
            data = json.load(open_file)

        for key, replacement in data.items():
            # Insert text and apply the "bold" tag to specific parts
            self.my_display_text.insert("end", "Key: ", "bold")
            self.my_display_text.insert("end", key, "normal")
            self.my_display_text.insert("end", "\n")
            self.my_display_text.insert("end", "Replacement: ", "bold")
            self.my_display_text.insert("end", replacement, "normal")
            self.my_display_text.insert("end", "\n\n")

    # Update Textbox with newly submitted keys and phrases
    def update_displayed_dict(self):
        # self.my_display_text.delete(1.0, "end")  # Clear the text widget
        for key, replacement in self.replacements_dict.items():
            self.my_display_text.insert("end", "Key: ", "bold")
            self.my_display_text.insert("end", key, "normal")
            self.my_display_text.insert("end", "\n")
            self.my_display_text.insert("end", "Replacement: ", "bold")
            self.my_display_text.insert("end", replacement, "normal")
            self.my_display_text.insert("end", "\n\n")

    def save_json(self):
        filename = 'replacements.json'
        try:
            if os.path.isfile(filename):
                # Load the existing JSON data
                with open(filename, 'r') as json_file:
                    existing_data = json.load(json_file)

                # Update the existing data with the new keys and replacements
                existing_data.update(self.replacements_dict)

                with open(filename, 'w') as json_file:
                    json.dump(existing_data, json_file, indent=4)
                    print("JSON data saved to file.")
            else:
                # If the file doesn't exist, just save the current data
                with open(filename, 'w') as json_file:
                    json.dump(self.replacements_dict, json_file, indent=4)
                    print("JSON data saved to file.")
                    # close the file
                    filename.close()
        except Exception as e:
            self.show_error_message(e)

    def init_text_replacement_gui(self):
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Create Button Frame
        button_frame_1 = ttk.Frame(self.frame, padding=5)
        button_frame_1.pack()

        # # Create Button Frame
        btn_phrase_submit = ttk.Button(button_frame_1,
                                       text="Submit",
                                       command=self.submit_key_replacement,
                                       style="mystyle.TButton")
        btn_phrase_submit.grid(row=0, column=0, padx=10, pady=15)

        # Create Key & Phrase 'Save All' Button
        btn_save = ttk.Button(button_frame_1,
                              text="Save All",
                              command=self.save_json,
                              style="mystyle.TButton")
        btn_save.grid(row=0, column=1, padx=10)

        # Create Key and Phrase Entry Frame
        key_phrase_entry_frame = ttk.Frame(self.frame, padding=5)
        key_phrase_entry_frame.pack(anchor=W, padx=43)
        # # Create Key and Phrase Entry Labels
        # key_phrase_label_frame = ttk.Frame(self.frame, padding=5)
        # key_phrase_label_frame.pack()

        # Create Key Entry
        self.key_input = tk.StringVar()  # Declaring String Variable
        self.key_entry = ttk.Entry(key_phrase_entry_frame,
                                   width=98,
                                   textvariable=self.key_input, )
        self.key_entry.grid(row=0, column=1)

        key_label = ttk.Label(key_phrase_entry_frame, text="Input Key: ", justify=LEFT, anchor=W)
        key_label.grid(row=0, column=0)

        # Create Phrase Entry
        self.phrase_input = tk.StringVar()
        self.phrase_entry = ttk.Entry(key_phrase_entry_frame,
                                      width=98,
                                      textvariable=self.phrase_input)
        self.phrase_entry.grid(row=1, column=1)

        phrase_label = ttk.Label(key_phrase_entry_frame, text="Input Replacement: ",
                                 padding=5,
                                 justify=LEFT,
                                 anchor=W)
        phrase_label.grid(row=1, column=0)

        # Create Textbox to Display JSON File Data
        self.my_display_text = tk.Text(self.frame,
                                       bg="#343638",  # Darker grey background color of textbox.
                                       width=100,
                                       height=30,
                                       bd=1,  # boarder width, making it small.
                                       fg="#d6d6d6",  # light grey color of the text.
                                       relief="flat",  # gets rid of the white line around the textbox.
                                       wrap=WORD,  # wraps whole words instead of partial words
                                       selectbackground="#1f538d"  # Bluish color when selecting text.
                                       )
        # Configure a "bold" tag
        self.my_display_text.configure(font=("Helvetica", 16, "bold"))

        self.my_display_text.pack()

    def pythonDict_to_json(self, replacements_dict):
        # Python dict
        # self.replacements_dict = {'Key': self.key_input, 'Replacement': self.phrase_input}
        print("This is Python", type(self.replacements_dict))

        print("\nNow Convert from Python to JSON")

        # Convert Python dict to JSON
        json_object = json.dumps(self.replacements_dict, indent=4)
        print("Converted to JSON", type(json_object))
        print(json_object)

    def show(self):
        self.frame.pack(fill='both', expand=True)


class TextReplacementLogic:  ##################################################################
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.replacements = {}  # Define Replacements Dictionary
        self.key_sequence = ""
        self.key_presses = 0  # Counter for the number of key presses without detection
        self.key_lengths = 0

    def replace_text(self, input_text):
        # Implement text replacement logic
        global restart_program_flag
        # global self.key_sequence, key_presses

        # Open and read the json file
        with open('replacements.json', 'r') as file:
            # replacements = dict(line.strip().split(':') for line in file)
            # Load in the json file
            replacements = json.load(file)

        self.key_lengths = {key: len(key) for key in replacements}

        def on_press(event):
            global restart_program_flag
            # global self.key_sequence, key_presses

            if event.name == "r" and keyboard.is_pressed("ctrl"):  # Check for Ctrl + R
                restart_program_flag = True
                return

            if event.event_type == keyboard.KEY_DOWN:
                key_name = event.name.lower()

                if key_name in ("enter", "shift", "space", "backspace", "alt", "caps"):
                    return

                self.key_sequence += key_name
                self.key_presses += 1  # Increment the counter
                print(f"Key pressed: {self.key_sequence}")

                for key in replacements:
                    if key in self.key_sequence:
                        self.remove_original_key_sequence(self.key_lengths.get(key, 0))
                        replacement = replacements[key]
                        self.replace_with_text(replacement)
                        print(f"Detected key press: {self.key_sequence} (Replaced with: {replacement})")
                        self.key_sequence = ""  # Reset the key sequence
                        self.key_presses = 0  # Reset the counter
                        return

        keyboard.on_press(on_press)

        try:
            while True:
                if self.key_presses >= 25:
                    print("Woah, We have more than 25 Key Presses!")
                    self.key_sequence = ""  # Reset the key sequence
                    self.key_presses = 0  # Reset the counter
                if restart_program_flag:
                    print("Program is Restarting...")
                    keyboard.unhook_all()
                    restart_program()
                    restart_program_flag = False  # Reset the restart flag
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # Create Function to 'backspace' same # of times as 'key' character length
    def remove_original_key_sequence(self, num_backspaces):
        for _ in range(num_backspaces):
            keyboard.press_and_release("backspace")

    # Remove 'key' and write the 'replacement'
    def replace_with_text(self, text):
        self.remove_original_key_sequence(self.key_lengths.get(self.key_sequence, 0))
        keyboard.write(text)

    # Function to restart program
    def restart_program(self):
        python = sys.executable
        os.startfile(__file__)
        time.sleep(0.4)
        sys.exit()

    def add_key(self, key):
        try:
            self.replacements[key] = ""
            self.save_json()
            print(f"Key '{key}' added")
        except Exception as e:
            print(f"Error adding key: {e}")

    def add_replacement(self, key, replacement):
        try:
            if key in self.replacements:
                self.replacements[key] = replacement
                self.save_json()
                print(f"Replacement for key '{key}' added.")
            else:
                print(f"Key Not Found")
        except Exception as e:
            print(f"Error adding replacement: {e}")


def show_error_message():
    error_text = str({e})
    messagebox.showerror("Error", error_text)


def main():
    # Create a thread for the GUI
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()

    # Start the key press detection in a separate thread
    keypress_thread = threading.Thread(target=run_keypress_detection)
    keypress_thread.daemon = True  # Allow the thread to be terminated when the main program exits
    keypress_thread.start()

    # Wait for the GUI thread to finish (blocks the main thread until the GUI is closed)
    gui_thread.join()


def run_gui():
    root = ThemedTk(theme="clearlooks")
    # root = tk.Tk()
    root.title("PT Bot")

    # Set App Size
    root.geometry("1200x800")

    # Set the dark theme style
    # sv_ttk.use_dark_theme()
    # #d6d6d6
    root.style = ttk.Style()
    root.style.configure(".",
                         background="#202121",
                         foreground="#d6d6d6",
                         relief="flat",
                         bd=1,
                         font="bold")
    root.style.configure('mystyle.TButton', font=('Arial', 12, 'bold'), foreground="#202121")
    root.style.configure('header.TLabel', font=('Helvetica', 20, 'bold'))
    root.style.configure('TLabel', font=('Helvetica', 14, 'bold'))

    # Create a frame to hold the notebook
    notebook_frame = ttk.Frame(root)
    notebook_frame.pack(fill="both", expand=True)

    # Create the Notebook widget
    notebook = ttk.Notebook(notebook_frame)
    chatbot_tab = ChatbotGUI(notebook)
    text_replacement_tab = TextReplacementGUI(notebook)

    # Add tabs to the Notebook
    notebook.add(chatbot_tab.frame, text="Chatbot")
    notebook.add(text_replacement_tab.frame, text="Text Replacement")
    notebook.pack(fill='both', expand=True)

    root.mainloop()


def run_keypress_detection():
    tr_logic = TextReplacementLogic(parent=None)
    tr_logic.replace_text(input_text=None)


if __name__ == '__main__':
    main()
