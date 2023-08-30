import importlib
import os
import subprocess
import sys
import textwrap
import time

import keyboard
from tkinter import *
from tkinter import ttk
import tkinter as tk
import google.generativeai as palm
import pickle
import sv_ttk
# import customtkinter
import json

restart_program_flag = False
key_sequence = ""
key_presses = 0  # Counter for the number of key presses without detection


class Chatbot:  ##################################################################

    def __init__(self, parent, my_text):
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
        try:
            full_conversation = self.full_conversation(user_input)
            if self.response is None:
                self.response = palm.chat(
                    model='models/chat-bison-001',
                    messages=full_conversation)
            else:
                self.response = self.response.reply(user_input)
            return self.response  # Return the last response from the model
        except Exception as e:
            return f"There was an error with bot_response: {e}"


class TextReplacement:
    class TextReplacementLogic:  ##################################################################
        def __init__(self, parent):
            self.parent = parent
            self.replacements = {}  # Define Replacements Dictionary

            pass

        def replace_text(self, input_text):
            # Implement text replacement logic
            global restart_program_flag, key_sequence, key_presses

            # Open and read the json file
            with open('replacements.json', 'r') as file:
                # replacements = dict(line.strip().split(':') for line in file)
                # Load in the json file
                replacements = json.load(file)

            key_lengths = {key: len(key) for key in replacements}

            def on_press(event):
                global restart_program_flag, key_sequence, key_presses

                if event.name == "r" and keyboard.is_pressed("ctrl"):  # Check for Ctrl + R
                    restart_program_flag = True
                    return

                if event.event_type == keyboard.KEY_DOWN:
                    key_name = event.name.lower()

                    if key_name in ("enter", "shift", "space", "backspace", "alt", "caps"):
                        return

                    key_sequence += key_name
                    key_presses += 1  # Increment the counter
                    print(f"Key pressed: {key_sequence}")

                    for key in replacements:
                        if key in key_sequence:
                            remove_original_key_sequence(key_lengths.get(key, 0))
                            replacement = replacements[key]
                            replace_with_text(replacement)
                            print(f"Detected key press: {key_sequence} (Replaced with: {replacement})")
                            key_sequence = ""  # Reset the key sequence
                            key_presses = 0  # Reset the counter
                            return

        def monitor_key_presses(self):
            global restart_program_flag, key_sequence, key_presses

            keyboard.on_press(on_press)

            try:
                while True:
                    if key_presses >= 25:
                        print("Woah, We have more than 25 Key Presses!")
                        key_sequence = ""  # Reset the key sequence
                        key_presses = 0  # Reset the counter
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
            remove_original_key_sequence(key_lengths.get(key_sequence, 0))
            keyboard.write(text)

        # Function to restart program
        def restart_program(self):
            python = sys.executable
            os.startfile(__file__)
            time.sleep(0.4)
            sys.exit()

        # def add_key(self, key):
        #     try:
        #         self.replacements[key] = ""
        #         self.save_json(self.replacements, 'replacements.json')
        #         print(f"Key '{key}' added")
        #     except Exception as e:
        #         print(f"Error adding key: {e}")
        #
        #
        # def add_replacement(self, key, replacement):
        #     try:
        #         if key in self.replacements:
        #             self.replacements[key] = replacement
        #             self.save_json(replacements, 'replacements.json')
        #             print(f"Replacement for key '{key}' added.")
        #         else:
        #             print(f"Key Not Found")
        #     except Exception as e:
        #         print(f"Error adding replacement: {e}")

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

    class TextReplacementGUI:  ##################################################################
        def __init__(self, parent):
            self.parent = parent
            self.frame = ttk.Frame(self.parent)
            self.init_text_replacement_gui()
            self.my_display_text = None
            self.key_entry = None
            self.key_input = tk.StringVar()
            self.phrase_entry = None
            self.phrase_input = tk.StringVar()
            self.json_filename = 'replacements.json'
            self.replacements = {}  # Define Replacements Dictionary

        def init_text_replacement_gui(self):
            self.frame.grid(row=0, column=0, sticky="nsew")
            # ... create text replacement GUI elements

            # Create Button Frame
            button_frame_1 = ttk.Frame(self.frame, padding=5)
            button_frame_1.pack()

            # # Create Button Frame
            btn_phrase_submit = ttk.Button(button_frame_1,
                                           text="Submit",
                                           command=self.gui.submit_key_replacement)
            btn_phrase_submit.grid(row=0, column=0, padx=10)

            # Create Key & Phrase 'Save All' Button
            btn_save = ttk.Button(button_frame_1,
                                  text="Save All",
                                  command=self.gui.save_json)
            btn_save.grid(row=0, column=1, padx=10)

            # Create Key and Phrase Entry Frame
            key_phrase_entry_frame = ttk.Frame(self.frame, padding=5)
            key_phrase_entry_frame.pack()

            # Create Key Entry
            self.key_input = tk.StringVar()  # Declaring String Variable
            self.key_entry = ttk.Entry(key_phrase_entry_frame,
                                       width=100,
                                       textvariable=self.gui.key_input)
            self.key_entry.grid(row=0, column=0)

            # Create Phrase Entry
            self.phrase_input = tk.StringVar()
            self.phrase_entry = ttk.Entry(key_phrase_entry_frame,
                                          width=100,
                                          textvariable=self.gui.phrase_input)
            self.phrase_entry.grid(row=1, column=0)

            # Create Textbox to Display JSON File Data
            self.my_display_text = tkinter.Text(self.frame,
                                                bg="#343638",  # Darker grey background color of textbox.
                                                width=100,
                                                height=30,
                                                bd=1,  # boarder width, making it small.
                                                fg="#d6d6d6",  # light grey color of the text.
                                                relief="flat",  # gets rid of the white line around the textbox.
                                                wrap=WORD,  # wraps whole words instead of partial words
                                                selectbackground="#1f538d"  # Bluish color when selecting text.
                                                )
            self.my_display_text.pack()

        # Create method from the GUI component to update the displayed data
        def gui_update_displayed_data(self):
            pass

        def show(self):
            self.frame.pack(fill='both', expand=True)

    def __init__(self):
        self.root = Tk()
        self.gui = self.TextReplacementGUI(self)
        self.logic = self.TextReplacementLogic(self)

    def run(self):
        self.root.mainloop()

    # 'Write' the 'key' and 'replacement' to the JSON file
    def submit_key_replacement(self, event=None):
        key_input = self.key_input.get()
        phrase_input = self.phrase_input.get()

        if key_input and phrase_input:
            try:
                self.add_key(key_input)
                self.add_replacement(key_input, phrase_input)
                print("Key and Replacement Added.")
            except Exception as e:
                self.show_error_message(e)

        else:
            print("You Forgot to Type Something!")

    def save_json(self):
        try:
            with open(self.json_filename, 'w') as json_file:
                json.dump(self.replacements, json_file, indent=4)
            print("JSON data saved to file.")
        except Exception as e:
            self.show_error_message(e)


class ChatbotGUI:  ##################################################################

    def __init__(self, parent):
        self.api_key = None
        self.user_input = None
        self.my_text = None
        self.api_entry = None
        self.chat_entry = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.init_chatbot_gui()
        self.chatbot_instance = Chatbot(self, self.my_text)

    def init_chatbot_gui(self):
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Configure row and column weights
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        # Create Text Frame
        text_frame = ttk.Frame(self.frame, padding=20)
        text_frame.grid(row=2, column=0, pady=5, padx=10, sticky="w")

        # Add Label for Chatbot Text Box
        text_box_label = ttk.Label(self.frame, justify=LEFT, anchor=W, padding=20, text="PT Chat Bot Discussion")
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
                                    textvariable=self.user_input,
                                    )
        self.chat_entry.grid(row=3, column=0)

        # Bind the <Return> key press event to the entry widget
        self.chat_entry.bind("<Return>", self.speak)

        # Create Button Frame
        button_frame = ttk.Frame(self.frame, padding=10)
        button_frame.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        # Style API button
        style = ttk.Style()
        style.configure('A.TButton',
                        font='underline',
                        boardwidth='2')

        # Create Submit Button
        submit_button = ttk.Button(button_frame,
                                   text="Speak To ChatBot",
                                   command=self.speak,
                                   width=30,
                                   style='A.TButton')
        submit_button.grid(row=0, column=0, padx=25, pady=10)

        # Create Clear Button
        clear_button = ttk.Button(button_frame,
                                  text="Clear Response",
                                  command=self.clear,
                                  width=20)
        clear_button.grid(row=0, column=1, padx=35, pady=10)

        # Create API Button
        api_button = ttk.Button(button_frame,
                                text="Update API Key",
                                command=self.key,
                                width=20)
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
                                   textvariable=self.api_key)
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

                    # Clear Users Textbox
                    self.chat_entry.delete(0, END)

                    self.my_text.insert(END, "You: " + user_input + "\n\n")
                    self.my_text.insert(END, "ChatBot: " + response.last + "\n\n")

                else:
                    # Create the file
                    with open(filename,
                              'wb') as input_file:  # 'wb' allows us to write the file name and create it for us
                        pass
                    # Close the File
                    input_file.close()
                    # Error Message - You need an API Key
                    self.my_text.insert(END,
                                        "\n\nYou Need An API Key To Talk With ChatBot. Get one here: "
                                        "\nhttps://developers.generativeai.google/guide/palm_api_overview")
            except Exception as e:
                error_message = f"There was an error: {e}"
                self.my_text.insert(END, error_message + "\n\n")

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
            self.parent.winfo_toplevel().geometry('1200x800')

        except Exception as e:
            self.my_text.insert(END, f"\n\n There was an error \n\n{e}")

    def show(self):
        self.frame.pack(fill='both', expand=True)


def show_error_message():
    error_text = str({e})
    messagebox.showerror("Error", error_text)


# outer = TextReplacement()
# d1 = outer.TextReplacementGUI


def main():
    root = Tk()
    root.title("PT Bot")

    # Set App Size
    root.geometry("1200x800")

    # Set the dark theme style
    sv_ttk.use_dark_theme()

    style = ttk.Style()
    style.configure(".",
                    background="black",
                    foreground="#d6d6d6",
                    relief="flat",
                    bd=1,
                    font='bold')

    # Create a frame to hold the notebook
    notebook_frame = ttk.Frame(root)
    notebook_frame.pack(fill="both", expand=True)

    # Create the Notebook widget
    notebook = ttk.Notebook(notebook_frame)
    chatbot_tab = ChatbotGUI(notebook)
    # text_replacement_tab = d1(notebook)

    # Create an instance of TextReplacement
    text_replacement_instance = TextReplacement()
    text_replacement_tab = text_replacement_instance.gui

    # Create an instance of TextReplacement
    # text_replacement_instance = TextReplacement()

    # Add tabs to the Notebook
    notebook.add(chatbot_tab.frame, text="Chatbot")
    notebook.add(text_replacement_tab.frame, text="Text Replacement")
    notebook.pack(fill='both', expand=True)

    root.mainloop()


if __name__ == '__main__':
    main()
    monitor_key_presses()  # Monitor key presses
