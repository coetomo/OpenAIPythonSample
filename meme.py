import os

import requests
from PIL import ImageFont, ImageDraw, Image

DEFAULT_PROMPT_MEME = "I want you to create a funny meme out of this picture. Please give me the captions (as top and bottom text) for the meme (don't say anything else, respond as {top text} new line char {bottom text}, don't add labels like top or bottom text, no NSFW words, and don't add quotes)"

def generate_meme_caption(url, text=DEFAULT_PROMPT_MEME, client=None):
    """
    Uses OpenAI API (GPT-4o Vision) to generate a caption for a meme from an online image.

    :param url: URL to the image
    :param text: Prompt for OpenAI API. The default prompt will produce captions as top and bottom text.
    :param client: OpenAI Client
    :return: the caption generated as a single string
    """
    if client is None:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()


def draw_text(draw, text, position, font_path, max_width, min_fontsize=40):
    fontsize = min_fontsize
    font = ImageFont.truetype(font_path, fontsize)

    # Repeat with larger font if it doesn't cover the minimum width covered
    while True:
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        # Split to multi-lines if it's too long
        for word in words:
            word_width = draw.textbbox((0, 0), word + " ", font=font)[2]
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))

        text_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)
        if text_width >= max_width * 0.85:
            break
        else:
            fontsize += 2
            font = ImageFont.truetype(font_path, fontsize)

    y_offset = position[1]
    # Draw each line of text
    for line in lines:
        _, _, line_width, text_height = draw.textbbox((0, 0), line, font=font)
        draw.text(((max_width - line_width) / 2 + position[0], y_offset), line, font=font, fill="white",
                  stroke_width=2, stroke_fill="black")
        y_offset += text_height + 10


def draw_captions(img, top_text, bottom_text, show_image=False, save_as=None):
    draw = ImageDraw.Draw(img)
    font_path = "assets/impact.ttf"
    max_width = img.width * 0.95

    # Draw the top caption
    top_y_position = 5
    draw_text(draw, top_text, (img.width * 0.025, top_y_position), font_path, max_width)

    # Draw the bottom caption
    bottom_y_position = img.height - 100
    draw_text(draw, bottom_text, (img.width * 0.025, bottom_y_position), font_path, max_width)

    if show_image:
        img.show()

    if save_as:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(save_as)
        print(f"Image saved as {save_as}!")

    return img


def memeify(url, caption=None, show_image=False, save_as=None):
    if caption is None:
        caption = generate_meme_caption(url)
    top, bot = caption.split("\n")

    img = Image.open(requests.get(url, stream=True).raw)
    meme_img = draw_captions(img, top, bot, show_image=show_image, save_as=save_as)

    return meme_img
