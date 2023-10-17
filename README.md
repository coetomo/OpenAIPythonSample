# Sample Python code using OpenAI API
A bare-bones project to showcase how you can utilize OpenAI API using Python. Check out their 
[API Reference](https://platform.openai.com/docs/api-reference) page to see what other things you can do 
with their API.

### Features
- Generate Image from prompt (using DALL-E model)
- Text Moderation
- Text and GUI modes (Tkinter)
- (more to come?)

*Requires OpenAI API key to be set as an environment variable:*

```bash
export OPENAI_API_KEY=####################
```

### How to run:

1) Ensure that the API key is set as an environment variable (or if you don't have one, 
obtain one from their [website](https://openai.com/blog/openai-api))

2) (Optional) Create a virtual environment

3) Install the necessary packages
    ```commandline
    pip install -r requirements.txt
    ```

4) There are two entry points to run and test the functionalities:
   - **main.py**: Terminal/Console based so all prompts and output will be displayed normally there.
   - **GUI.py**: Tkinter based so all prompts and output will be displayed in a GUI.


Feel free to fork or create pull request to add/change its functionalities 😀