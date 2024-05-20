import itertools
import os
import threading
import tkinter as tk
from tkinter import messagebox

import openai
import requests
from PIL import Image, ImageTk

from main import generate_image, moderate, memeify

openai.api_key = os.getenv("OPENAI_API_KEY")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenAI Python")
        self.geometry("400x250")
        self.choice = tk.StringVar(value='image')

        label = tk.Label(self, text="Choose an option:", font=("Arial", 14))
        label.pack(pady=10)

        image_button = tk.Radiobutton(self, text="Generate Image", variable=self.choice, value="image",
                                      font=("Arial", 12))
        image_button.pack()

        text_button = tk.Radiobutton(self, text="Moderate Text", variable=self.choice, value="text",
                                     font=("Arial", 12))
        text_button.pack()

        meme_button = tk.Radiobutton(self, text="Generate Meme", variable=self.choice, value="meme",
                                     font=("Arial", 12))
        meme_button.pack()

        self.text_entry = tk.Entry(self, width=40, font=("Arial", 12))
        self.text_entry.pack(pady=10)

        submit_button = tk.Button(self, text="Submit", command=self.process_choice,
                                  font=("Arial", 12))
        submit_button.pack()

    def show_loading(self):
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Loading")
        self.loading_window.geometry("200x100")
        self.loading_window.resizable(False, False)

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

        # Add loading label with animation
        self.loading_label = tk.Label(self.loading_window, text="Loading", font=("Arial", 14))
        self.loading_label.pack(expand=True)
        self.animate_loading()

    def animate_loading(self):
        self.loading_text = itertools.cycle(["Loading", "Loading.", "Loading..", "Loading..."])
        self.update_loading_text()

    def update_loading_text(self):
        if hasattr(self, 'loading_label') and self.loading_label.winfo_exists():
            self.loading_label.config(text=next(self.loading_text))
            self.loading_window.after(500, self.update_loading_text)

    def hide_loading(self):
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def process_choice(self):
        choice = self.choice.get()
        user_input = self.text_entry.get()

        threading.Thread(target=self._process_choice, args=(choice, user_input)).start()

    def _process_choice(self, choice, user_input):
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
        if url:
            response = requests.get(url, stream=True)
            img = Image.open(response.raw)

        img = img.resize((768, 768), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        image_window = tk.Toplevel(self)
        image_window.title("Generated Image")
        panel = tk.Label(image_window, image=img)
        panel.image = img
        panel.pack()

    def display_output(self, output):
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
                category_value_label.config(fg="red")
            else:
                category_value_label.config(fg="green")

            if key in output["category_scores"]:
                score_value_label = tk.Label(result_window, text=f'{output["category_scores"][key]:.6f}',
                                             font=("Arial", 14))
                score_value_label.grid(row=row_number, column=2, padx=10, pady=5, sticky="w")

            row_number += 1


if __name__ == "__main__":
    app = App()
    app.mainloop()
