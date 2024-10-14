import itertools
import os
import threading
import tkinter as tk
from tkinter import messagebox
import openai
import requests
from PIL import Image, ImageTk
import speech_recognition as sr

from main import generate_image, moderate, memeify
from settings import *  # Import constants from settings

# This is a BYO-OpenAPI-key project. Read the README file for more info.
openai.api_key = os.getenv("OPENAI_API_KEY")


class App(tk.Tk):
    def __init__(self):
        """
        Initializes the main application window with various options for the user.
        """
        super().__init__()
        self.loading_label = None  # Placeholder for the loading label
        self.title("OpenAI Python")
        self.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")  # Use constant for dimensions
        self.choice = tk.StringVar(value='image')  # Tracks the selected option (image, text, or meme)

        # Create and display a label for instructions
        label = tk.Label(self, text="Choose an option:", font=("Arial", BASE_FONTSIZE + 3))
        label.pack(pady=10)

        # Radio buttons for selecting options
        image_button = tk.Radiobutton(self, text="Generate Image", variable=self.choice, value="image",
                                       font=("Arial", BASE_FONTSIZE))
        image_button.pack()

        text_button = tk.Radiobutton(self, text="Moderate Text", variable=self.choice, value="text",
                                      font=("Arial", BASE_FONTSIZE))
        text_button.pack()

        meme_button = tk.Radiobutton(self, text="Generate Meme", variable=self.choice, value="meme",
                                      font=("Arial", BASE_FONTSIZE))
        meme_button.pack()

        # Frame for user text input
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=10)

        # Text input box for user input
        self.text_entry = tk.Text(entry_frame, width=40, height=TEXT_ENTRY_MIN_HEIGHT,
                                   font=("Arial", BASE_FONTSIZE), wrap="word")
        self.text_entry.pack(side="left")
        self.text_entry.bind("<KeyRelease>", self.adjust_textbox_height)

        # Load microphone icon for the speech-to-text button
        mic_image = Image.open("icon-mic.png")
        mic_image = mic_image.resize((24, 24), Image.LANCZOS)  # Resize the icon if needed
        self.mic_icon = ImageTk.PhotoImage(mic_image)

        # Button for speech recognition
        self.speech_button = tk.Button(entry_frame, image=self.mic_icon, command=self.speech_to_text)
        self.speech_button.pack(side="left", padx=5)

        # Submit button to process user input
        submit_button = tk.Button(self, text="Submit", command=self.process_choice,
                                  font=("Arial", BASE_FONTSIZE))
        submit_button.pack()

    def adjust_textbox_height(self, event=None):
        """
        Adjusts the height of the text entry widget based on the number of lines.
        """
        num_lines = int(self.text_entry.index('end-1c').split('.')[0])
        self.text_entry.config(height=min(max(TEXT_ENTRY_MIN_HEIGHT, num_lines), TEXT_ENTRY_MAX_HEIGHT))

    def speech_to_text(self):
        """
        Converts speech to text using the microphone and fills the text entry with the result.
        """
        recognizer = sr.Recognizer()
        self.speech_button.config(bg="yellow")  # Indicate that the app is listening
        self.update_idletasks()

        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                self.text_entry.delete("1.0", tk.END)
                self.text_entry.insert("1.0", text)
                self.adjust_textbox_height()  # Adjust height after inserting text
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand the audio.")
            except sr.RequestError:
                messagebox.showerror("Error", "Error with the speech recognition service.")
            finally:
                self.speech_button.config(bg="SystemButtonFace")  # Reset button color

    def show_loading(self):
        """
        Displays a loading window while processing the user's request.
        """
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Loading")
        self.loading_window.geometry(f"{LOADING_WINDOW_WIDTH}x{LOADING_WINDOW_HEIGHT}")  # Use constant for dimensions
        self.loading_window.resizable(False, False)

        # Center the loading window on the main app window
        self.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_w = self.winfo_width()
        main_h = self.winfo_height()
        loading_w = self.loading_window.winfo_width()
        loading_h = self.loading_window.winfo_height()
        pos_x = main_x + (main_w // 2) - (loading_w // 2)
        pos_y = main_y + (main_h // 2) - (loading_h // 2)
        self.loading_window.geometry(f"+{pos_x}+{pos_y}")

        # Loading label with animation
        self.loading_label = tk.Label(self.loading_window, text="Loading", font=("Arial", 14))
        self.loading_label.pack(expand=True)
        self.animate_loading()

    def animate_loading(self):
        """
        Cycles through loading messages to create an animation effect.
        """
        self.loading_text = itertools.cycle(["Loading", "Loading.", "Loading..", "Loading..."])
        self.update_loading_text()

    def update_loading_text(self):
        """
        Updates the loading label's text for the animation.
        """
        if hasattr(self, 'loading_label') and self.loading_label.winfo_exists():
            self.loading_label.config(text=next(self.loading_text))
            self.loading_window.after(500, self.update_loading_text)

    def hide_loading(self):
        """
        Closes the loading window.
        """
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def process_choice(self):
        """
        Starts a new thread to process the user's choice and input.
        """
        choice = self.choice.get()
        user_input = self.text_entry.get("1.0", tk.END).strip()

        # Run the processing function in a separate thread to keep the UI responsive
        threading.Thread(target=self._process_choice, args=(choice, user_input)).start()

    def _process_choice(self, choice, user_input):
        """
        Processes the user's choice (image generation, text moderation, or meme creation).
        """
        self.show_loading()
        try:
            if choice == "image":
                url = None
                try:
                    url = generate_image(user_input)
                except Exception as e:
                    messagebox.showerror("Error", f"Image generation failed: {str(e)}")
                if url:
                    self.show_image(url)
                else:
                    messagebox.showerror("Error", "Image generation failed!")

            elif choice == "text":
                output = moderate(user_input)
                self.display_output(output)

            elif choice == "meme":
                try:
                    meme_img = memeify(user_input)
                    self.show_image(img=meme_img)
                except Exception as e:
                    messagebox.showerror("Error", f"Meme generation failed: {str(e)}")
        finally:
            self.hide_loading()

    def show_image(self, url=None, img=None):
        """
        Displays an image in a new window. Supports both URL and Image objects.
        """
        if url:
            response = requests.get(url, stream=True)
            img = Image.open(response.raw)

        # Resize the image if it's too large or too small
        if img.height < IMAGE_MIN_HEIGHT or img.height > IMAGE_MAX_HEIGHT:
            aspect_ratio = img.width / img.height
            new_height = IMAGE_MIN_HEIGHT
            new_width = int(new_height * aspect_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        img = ImageTk.PhotoImage(img)
        image_window = tk.Toplevel(self)
        image_window.title("Generated Image")
        panel = tk.Label(image_window, image=img)
        panel.image = img  # Store a reference to prevent garbage collection
        panel.pack()

    def display_output(self, output):
        """
        Displays the results of text moderation in a new window.
        """
        result_window = tk.Toplevel(self)
        result_window.title("Text Moderation Result")

        result_label = tk.Label(result_window, text="Result:", font=("Arial", 18, "bold"))
        result_label.grid(row=0, column=0, columnspan=3, pady=10)

        row_number = 1
        categories_title_label = tk.Label(result_window, text="Categories", font=("Arial", 16, "bold"))
        categories_title_label.grid(row=row_number, column=0, padx=10, pady=5, sticky="w")

        scores_title_label = tk.Label(result_window, text="Scores", font=("Arial", 16, "bold"))
        scores_title_label.grid(row=row_number, column=2, padx=10, pady=5, sticky="w")

        row_number += 1
        for key, value in output["categories"].items():
            category_label = tk.Label(result_window, text=key, font=("Arial", 14))
            category_label.grid(row=row_number, column=0, padx=10, pady=5, sticky="w")

            category_value_label = tk.Label(result_window, text=str(value), font=("Arial", 14))
            category_value_label.grid(row=row_number, column=1, padx=10, pady=5, sticky="w")
            if value:
                category_value_label.config(fg="red")  # Highlight in red if the category is flagged
            else:
                category_value_label.config(fg="green")  # Green if the category is safe

            if key in output["category_scores"]:
                score_value_label = tk.Label(result_window, text=f'{output["category_scores"][key]:.6f}',
                                             font=("Arial", 14))
                score_value_label.grid(row=row_number, column=2, padx=10, pady=5, sticky="w")

            row_number += 1


if __name__ == "__main__":
    app = App()
    app.mainloop()
