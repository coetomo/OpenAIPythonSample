# Sample Python code using OpenAI API
A bare-bones project to showcase how you can utilize OpenAI API using Python. Check out their 
[API Reference](https://platform.openai.com/docs/api-reference) page to see what other things you can do 
with their API. Tested using Windows 10-11 with Python 3.7 & 3.12.

### Features
- Generate Image from prompt (using DALL-E model)
- Speech-to-Text (SpeechRecognition + PyAudio)
- Text Moderation
- Text and GUI modes (Tkinter)
- Generate captions for images/memes
- Translate foreign language audio into English text
- (more to come?)


### Disclaimer
*Requires OpenAI API key to be set as an environment variable:*

```bash
export OPENAI_API_KEY=####################
```
This project does not provide free-to-use-for-everyone API. You can get your very own API-key easily
by signing up a free account from OpenAI website (see below).


### How to run:

1) Ensure that the API key is set as an environment variable (or if you don't have one, 
obtain one from their [website](https://openai.com/blog/openai-api))

2) (Optional) Create a virtual environment

3) Install the necessary packages
    ```commandline
    pip install -r requirements.txt
    ```
   If you're experiencing any issues installing PyAudio on a Windows machine and/or using 
   Python 3.7, you may try using the wheel (.whl) inside the `install` directory. Use
   `pip install <wheel-file>`.
4) There are two entry points to run and test the functionalities:
   - **main.py**: Terminal/Console based so all prompts and output will be displayed normally there.
   - **GUI.py**: Tkinter based so all prompts and output will be displayed in a GUI.


Feel free to fork or create pull request to add/change its functionalities 😀