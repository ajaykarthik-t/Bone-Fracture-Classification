import os
import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime
import pandas as pd

# Import the prediction function from your existing module
# If this import doesn't work directly, you'll need to ensure the file is in the same directory
# or modify your import structure
from predictions import predict

# Set page configuration
st.set_page_config(
    page_title="Bone Fracture Detection",
    page_icon="🦴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Define paths
project_folder = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(project_folder, 'images')

# Function to save results to CSV
def save_result_to_csv(image_name, bone_type, result):
    # Create directory if it doesn't exist
    results_dir = os.path.join(project_folder, 'PredictResults')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create or load existing CSV
    csv_path = os.path.join(results_dir, 'prediction_history.csv')
    
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = pd.DataFrame(columns=['Date', 'Image Name', 'Bone Type', 'Result'])
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        df = pd.DataFrame(columns=['Date', 'Image Name', 'Bone Type', 'Result'])
    
    # Add new row
    new_row = {
        'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Image Name': image_name,
        'Bone Type': bone_type,
        'Result': result
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save to CSV
    try:
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")
        return False

# Function to get download link for an image
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">📥 {text}</a>'
    return href

# Add custom CSS
st.markdown("""
<style>
    .header {
        color: #4A4A4A;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 30px;
        text-align: center;
    }
    .result-normal {
        color: #28a745;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .result-fractured {
        color: #dc3545;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .bone-type {
        color: #17a2b8;
        font-size: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .info-text {
        text-align: center;
        font-size: 18px;
        margin: 15px 0;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Main app layout
st.markdown('<div class="header">🦴 Bone Fracture Detection</div>', unsafe_allow_html=True)

# Info section
with st.expander("ℹ️ About This Application"):
    st.markdown("""
    This application uses machine learning to detect bone fractures in X-ray images.
    
    ### How to use:
    1. Upload an X-ray image using the file uploader below
    2. Click the "Predict" button to analyze the image
    3. View the results showing bone type and fracture status
    4. Save the results for your records
    
    ### Supported bone types:
    - Wrist
    - Elbow
    - Shoulder
    - Hand
    - Knee
    """)
    
    # Display rules image if it exists
    rules_path = os.path.join(folder_path, "rules.jpeg")
    if os.path.exists(rules_path):
        rules_img = Image.open(rules_path)
        st.image(rules_img, caption="Guidelines for X-ray Analysis", use_column_width=True)

st.markdown('<p class="info-text">Upload an X-ray image for fracture detection</p>', unsafe_allow_html=True)

# Create a placeholder for the uploaded image
image_placeholder = st.empty()

# Default image (Question Mark)
default_img_path = os.path.join(folder_path, "Question_Mark.jpg")
if os.path.exists(default_img_path):
    default_img = Image.open(default_img_path)
    image_placeholder.image(default_img, width=256)

# File uploader
uploaded_file = st.file_uploader("Choose an X-ray image...", type=["jpg", "jpeg", "png"])

# Initialize session state if not already initialized
if 'bone_type' not in st.session_state:
    st.session_state.bone_type = ""
if 'result' not in st.session_state:
    st.session_state.result = ""
if 'filename' not in st.session_state:
    st.session_state.filename = ""
if 'image' not in st.session_state:
    st.session_state.image = None
if 'prediction_done' not in st.session_state:
    st.session_state.prediction_done = False

# Process the uploaded file
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    
    # Resize image for display while maintaining aspect ratio
    width, height = image.size
    new_height = 256
    new_width = int(new_height / height * width)
    resized_image = image.resize((new_width, new_height))
    
    # Update the image in the placeholder
    image_placeholder.image(resized_image, width=new_width)
    
    # Save filename and image to session state
    st.session_state.filename = uploaded_file.name
    st.session_state.image = image
    
    # Reset prediction results when a new image is uploaded
    st.session_state.bone_type = ""
    st.session_state.result = ""
    st.session_state.prediction_done = False

# Create two columns for buttons
col1, col2 = st.columns(2)

# Predict button
predict_clicked = col1.button("Predict", type="primary", use_container_width=True)

# Placeholder for the results
results_placeholder = st.empty()

# Process prediction
if predict_clicked and uploaded_file is not None:
    # Save the uploaded file temporarily
    temp_file_path = os.path.join(project_folder, "temp_image.jpg")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Show a spinner while predicting
    with st.spinner("Analyzing X-ray image..."):
        # Get bone type
        try:
            bone_type_result = predict(temp_file_path, "Parts")
            st.session_state.bone_type = bone_type_result
            
            # Get fracture status
            fracture_result = predict(temp_file_path, bone_type_result)
            st.session_state.result = fracture_result
            st.session_state.prediction_done = True
        except Exception as e:
            st.error(f"Error during prediction: {e}")
            st.session_state.prediction_done = False
    
    # Clean up the temporary file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

# Save button (only show if prediction is done)
save_clicked = col2.button("Save Result", type="secondary", use_container_width=True, disabled=not st.session_state.prediction_done)

# Display results if prediction has been done
if st.session_state.prediction_done:
    results_html = f'<div class="bone-type">Type: {st.session_state.bone_type}</div>'
    
    if st.session_state.result == 'fractured':
        results_html += f'<div class="result-fractured">Result: Fractured</div>'
    else:
        results_html += f'<div class="result-normal">Result: Normal</div>'
    
    results_placeholder.markdown(results_html, unsafe_allow_html=True)

# Handle saving results
if save_clicked and st.session_state.prediction_done and st.session_state.image is not None:
    # Create a results image with text overlay for download
    img = st.session_state.image.copy()
    
    # Save to CSV
    save_success = save_result_to_csv(
        st.session_state.filename,
        st.session_state.bone_type,
        st.session_state.result
    )
    
    if save_success:
        st.success("Results saved successfully!")
        
        # Create a download link for the original image
        st.markdown(
            get_image_download_link(
                img, 
                f"bone_fracture_{st.session_state.bone_type}_{st.session_state.result}.png",
                "Download Result Image"
            ),
            unsafe_allow_html=True
        )
        
        # Show download link for the CSV
        csv_path = os.path.join(project_folder, 'PredictResults', 'prediction_history.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'rb') as f:
                csv_data = f.read()
            
            b64 = base64.b64encode(csv_data).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="prediction_history.csv">📊 Download Complete Prediction History</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("Failed to save results. Please try again.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6c757d; font-size: 14px;">
        Bone Fracture Detection System | Created with Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)