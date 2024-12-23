from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
from gtts import gTTS
import tempfile

load_dotenv()
# Configure Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Replace with your actual API key

# Set up configurations
UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Google Generative AI Model
model = genai.GenerativeModel("learnlm-1.5-pro-experimental")

def limit_text_length(text, max_chars=700):
    # Ensure the TTS reads only the first max_chars characters or up to a sentence boundary
    if len(text) <= max_chars:
        return text
    else:
        truncated_text = text[:max_chars]
        last_period_index = truncated_text.rfind(".")  # Find the last full sentence
        if last_period_index != -1:
            return truncated_text[:last_period_index + 1]
        return truncated_text

# Function to summarize and process image text
def process_image(image_path):
    img = Image.open(image_path)
    res = model.generate_content(img)
    response_text = res.text

    # Summarize the text
    summary_text = limit_text_length(response_text, max_chars=1000)

    # Text-to-Speech using gTTS
    tts = gTTS(text=summary_text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        st.audio(temp_audio.name)  # Use Streamlit to play the audio

# Streamlit UI
st.set_page_config(page_title="ImageNarrator", layout="centered")
st.title("ImageNarrator")
st.write("Upload an image or click a picture using your camera to read it aloud.")

# Option for file upload or camera input
st.write("Choose an option:")
option = st.radio("Select input method:", ("Upload Image", "Use Camera"))

if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Display the uploaded image
        st.image(file_path, caption="Uploaded Image", use_container_width=True)

        # Process the image
        st.write("Processing the image...")
        try:
            process_image(file_path)
            st.success("Done reading the text.")
        except Exception as e:
            st.error("An error occurred while processing the image.")
            st.write(str(e))

elif option == "Use Camera":
    camera_file = st.camera_input("Take a picture")

    if camera_file:
        # Save the captured image
        file_path = os.path.join(UPLOAD_FOLDER, "captured_image.jpg")
        with open(file_path, "wb") as f:
            f.write(camera_file.getbuffer())

        # Display the captured image
        st.image(file_path, caption="Captured Image", use_container_width=True)

        # Process the image
        st.write("Processing the image...")
        try:
            process_image(file_path)
            st.success("Done reading the text.")
        except Exception as e:
            st.error("An error occurred while processing the image.")
            st.write(str(e))
