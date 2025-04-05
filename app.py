import os
import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import time

# Assuming predictions.py contains the predict function
try:
    from predictions import predict
except ImportError:
    # Create a mock prediction function for demo purposes
    def predict(img_path, prediction_type=None):
        if prediction_type == "Parts":
            return "Wrist"
        else:
            # For demo purposes
            import random
            return random.choice(['fractured', 'normal'])

# Set page config
st.set_page_config(
    page_title="Bone Fracture Detection",
    page_icon="🦴",
    layout="centered"
)

# Global variables
project_folder = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(project_folder, 'images/')

# Custom CSS for refined styling
st.markdown("""
    <style>
    /* Overall refined look */
    body {
        background-color: #f8f9fa;
        color: #333;
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    
    .main {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    .header {
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eaeaea;
    }
    
    .title {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    
    .subtitle {
        color: #7f8c8d;
        font-size: 16px;
    }
    
    /* Results styling */
    .result-normal {
        color: #27ae60;
        font-size: 24px;
        font-weight: bold;
        padding: 15px;
        background-color: #e8f8f0;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(39, 174, 96, 0.2);
        border-left: 5px solid #27ae60;
    }
    
    .result-fractured {
        color: #e74c3c;
        font-size: 24px;
        font-weight: bold;
        padding: 15px;
        background-color: #fceae9;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(231, 76, 60, 0.2);
        border-left: 5px solid #e74c3c;
    }
    
    .bone-type {
        font-size: 20px;
        font-weight: bold;
        color: #3498db;
        text-align: center;
        margin: 15px 0;
        padding: 10px;
        background-color: #e8f4fc;
        border-radius: 8px;
    }
    
    /* Image container */
    .image-container {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #eaeaea;
        margin: 15px 0;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #bdc3c7;
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        background-color: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #3498db;
        background-color: #e8f4fc;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #3498db !important;
    }
    
    /* Download button */
    .download-btn {
        display: inline-block;
        padding: 10px 20px;
        background-color: #3498db;
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .download-btn:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Progress bar styling */
    div.stProgressBar > div {
        background-color: #3498db;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper function to get image download link
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

# Main function
def main():
    # Header
    st.markdown(
        '<div class="header">'
        '<div class="title">🦴 Bone Fracture Detection</div>'
        '<div class="subtitle">Upload an X-ray image for quick analysis</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Two columns layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'])
        
        # Display uploaded image
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            img = Image.open(uploaded_file)
            img_path = os.path.join(project_folder, "temp_upload.jpg")
            img.save(img_path)
            
            # Display the image with better styling
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(img, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show placeholder with better styling
            st.markdown(
                '<div class="upload-area">'
                '<p>📤 Drag and drop an X-ray image here</p>'
                '<p>or</p>'
                '<p>Click "Browse files" above</p>'
                '</div>', 
                unsafe_allow_html=True
            )
            
            # Optionally show a placeholder image
            try:
                placeholder_image = Image.open(os.path.join(folder_path, "Question_Mark.jpg"))
                st.image(placeholder_image, width=200)
            except FileNotFoundError:
                pass
    
    with col2:
        if uploaded_file is not None:
            st.markdown("### Analysis")
            
            # Analyze button
            if st.button("Analyze X-ray", use_container_width=True):
                with st.spinner("Processing..."):
                    # Progress bar with better styling
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)  # Simulate processing time
                        progress_bar.progress(i + 1)
                    
                    # Make prediction
                    bone_type = predict(img_path, "Parts")
                    result = predict(img_path, bone_type)
                
                # Display results with better styling
                st.markdown(f'<div class="bone-type">Type: {bone_type}</div>', unsafe_allow_html=True)
                
                if result == 'fractured':
                    st.markdown('<div class="result-fractured">Result: Fractured</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="result-normal">Result: Normal</div>', unsafe_allow_html=True)
                
                # Download result option
                result_img = img.copy()  # Just using the original image for simplicity
                download_link = get_image_download_link(result_img, "fracture_result.png", "💾 Save Result")
                st.markdown(f"<div style='text-align: center;'>{download_link}</div>", unsafe_allow_html=True)
        else:
            # Brief instructions
            st.markdown("### How it works")
            st.markdown("""
            1. Upload an X-ray image 
            2. Click "Analyze X-ray"
            3. View bone type and fracture status
            4. Save results if needed
            """)
            
            # Sample result (optional)
            st.markdown("### Sample Result")
            st.markdown('<div class="bone-type">Type: Wrist</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-normal">Result: Normal</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()