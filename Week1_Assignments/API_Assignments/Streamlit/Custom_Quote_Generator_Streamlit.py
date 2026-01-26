# streamlit_motivation_centered.py

import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

# -------------------------------
# Quotes list
# -------------------------------
motivational_quotes = [
    "Hard work beats talent when talent doesn’t work hard.",
    "Commitment is the foundation of great achievements.",
    "Every day of learning makes you stronger.",
    "Discipline is the bridge between goals and accomplishments.",
    "Wisdom comes from experience, and experience comes from action.",
    "Your effort today shapes your success tomorrow.",
    "Consistency and dedication always pay off.",
    "Start small, stay focused, and keep improving."
]

# -------------------------------
# Function to get a random quote
# -------------------------------
def get_random_quote():
    return random.choice(motivational_quotes)

# -------------------------------
# Function to overlay wrapped text on image
# -------------------------------
def add_text_to_image(img_url, text):
    # Load image
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Create editable layer
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Font
    try:
        font_size = int(img.size[1] / 15)
        font = ImageFont.truetype("arial.ttf", size=font_size)
    except:
        font = ImageFont.load_default()
        font_size = 20

    # Wrap text to fit image width
    max_width = int(img.size[0] * 0.8)
    lines = textwrap.wrap(text, width=40)
    while True:
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_widths.append(bbox[2] - bbox[0])
        if max(line_widths) <= max_width:
            break
        lines = textwrap.wrap(text, width=int(len(lines[0]) * 0.9))

    # Compute line height
    line_height = (draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]) + 5
    total_text_height = line_height * len(lines)

    # Position: bottom center
    y = img.size[1] - total_text_height - 50
    x_center = img.size[0] / 2

    # Draw each line centered
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        # shadow
        draw.text((x_center - line_width / 2 + 2, y + 2), line, font=font, fill=(0, 0, 0, 180))
        # main text
        draw.text((x_center - line_width / 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height

    combined = Image.alpha_composite(img, txt_layer)
    return combined

# -------------------------------
# Streamlit page configuration
# -------------------------------
st.set_page_config(
    page_title="Your morning dose of motivation",
    page_icon="🌅",
    layout="wide"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
    <style>
    body {
        background-color: #fff7f0;
    }
    .main-header {
        font-size: 40px;
        font-weight: bold;
        color: #ff6f61;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 22px;
        text-align: center;
        color: #333333;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        font-size: 18px;
        padding: 8px 24px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Session state
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "quote" not in st.session_state:
    st.session_state.quote = ""

# -------------------------------
# Login Page
# -------------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="main-header">Your morning dose of motivation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Login to see your personalized quote!</div>', unsafe_allow_html=True)

    username_input = st.text_input("Enter your name:")
    if st.button("Login"):
        if username_input.strip() != "":
            st.session_state.logged_in = True
            st.session_state.username = username_input.strip()
            st.session_state.quote = get_random_quote()
        else:
            st.warning("Please enter your name to continue.")

# -------------------------------
# Welcome Page
# -------------------------------
else:
    st.markdown(f'<div class="main-header">Good Morning, {st.session_state.username}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Here is your daily dose of motivation!</div>', unsafe_allow_html=True)

    img_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1350&q=80"
    img_with_quote = add_text_to_image(img_url, st.session_state.quote)

    # Center image using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img_with_quote, width=700)
