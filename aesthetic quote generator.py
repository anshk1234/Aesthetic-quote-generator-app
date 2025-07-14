import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, random, pathlib, tempfile
from quotes import quotes_list  # External quote file
import time
import json
from streamlit_lottie import st_lottie

# ----- CONFIG -----
st.set_page_config(page_title="Aesthetic Quote Forge", layout="centered")
st.title("🌸 Aesthetic Quote Forge")

# --- Splash Animation ---
def load_lottiefile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    lottie_intro = load_lottiefile("loading.json")
    splash = st.empty()
    with splash.container():
        st.markdown("<h1 style='text-align:center;'>Welcome to QUOTE GENERATOR!</h1>", unsafe_allow_html=True)
        st_lottie(lottie_intro, height=280, speed=1.0, loop=False)
        time.sleep(2)
    splash.empty()
    st.session_state.show_intro = False

    
# ----- INITIALIZE SESSION QUOTE -----
if "selected_quote" not in st.session_state:
    st.session_state.selected_quote = random.choice(quotes_list)

# ----- FOLDER SETUP -----
ASSET_FOLDER = "assets"
FONT_FOLDER = "fonts"

# Load assets
backgrounds = [f for f in os.listdir(ASSET_FOLDER) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
fonts_available = [f for f in os.listdir(FONT_FOLDER) if f.lower().endswith(".ttf")]

# ----- SIDEBAR OPTIONS -----
st.sidebar.header("🛠 Customize")

mode = st.sidebar.radio("Quote Mode", ["Type Your Own", "Random"])

# Manual refresh for random quote
if mode == "Random" and st.sidebar.button("🔁 Get New Quote"):
    st.session_state.selected_quote = random.choice(quotes_list)

# Get current quote
quote_text = st.sidebar.text_area("Your Quote", "") if mode == "Type Your Own" else st.session_state.selected_quote

bg_choice = st.sidebar.selectbox("Background Wallpaper", backgrounds)
selected_font = st.sidebar.selectbox("Font Style", fonts_available)
font_size = st.sidebar.slider("Font Size", 20, 80, 40)

# ----- PREVIEW + DOWNLOAD -----
if quote_text.strip():
    try:
        # Load background
        bg_path = os.path.join(ASSET_FOLDER, bg_choice)
        image = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Load font
        font_path = os.path.join(FONT_FOLDER, selected_font)
        font = ImageFont.truetype(font_path, font_size)

        # Word wrap logic
        def wrap_text(text, max_chars):
            words = text.split()
            lines, line = [], ""
            for word in words:
                if len(line + word) <= max_chars:
                    line += word + " "
                else:
                    lines.append(line)
                    line = word + " "
            lines.append(line)
            return "\n".join(lines)

        wrapped = wrap_text(quote_text.strip(), 40)

        # Center text
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Shadow + quote
        draw.multiline_text((x+2, y+2), wrapped, font=font, fill=(0, 0, 0, 120), align="center")
        draw.multiline_text((x, y), wrapped, font=font, fill=(255, 255, 255), align="center")

        # Save preview to system temp folder
        temp_dir = tempfile.gettempdir()
        preview_path = os.path.join(temp_dir, "aesthetic_quote_preview.png")
        image.save(preview_path)

        # Display in app
        st.image(image, caption="🌟 Live Preview", use_container_width=True)

        # Download button: save to Downloads only on click
        with open(preview_path, "rb") as f:
            if st.download_button("📥 Download as PNG", data=f, file_name="aesthetic_quote.png", mime="image/png"):
                downloads_path = pathlib.Path.home() / "Downloads"
                final_path = os.path.join(downloads_path, "aesthetic_quote.png")
                image.save(final_path)

    except OSError as e:
        st.error(f"🚫 Font error: {e}")
else:
    st.info("📝 Type a quote or select Random to preview your aesthetic creation.")
