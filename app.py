from flask import Flask, request, jsonify
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import io
import os

# Configure Gemini API
load_dotenv()
api_key = os.getenv("API_KEY")  # Replace with your API key if not using environment variables
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Flask app
app = Flask(__name__)

def to_plain_text(text):
    """
    Clean and format prescription text for better readability
    """
    # Remove asterisks used as markers
    text = text.replace(':*', ':')
    text = text.replace('*', '')
    
    # Split into sections
    sections = [
        'Medicine Name:',
        'Symptoms:',
        'Primary Diagnosis',
        'Usage',
        'Dosage:',
        'Important Note:'
    ]
    
    # Clean and format each section
    result = []
    current_text = text
    
    for section in sections:
        if section in current_text:
            # Find the section and its content
            start = current_text.find(section)
            next_section_start = float('inf')
            
            # Find the next section's start if it exists
            for next_section in sections:
                pos = current_text.find(next_section, start + len(section))
                if pos != -1 and pos < next_section_start:
                    next_section_start = pos
            
            # Extract content
            if next_section_start != float('inf'):
                content = current_text[start:next_section_start].strip()
            else:
                content = current_text[start:].strip()
                
            # Format section
            formatted_section = f"- {content}"
            result.append(formatted_section)
    
    return '\n\n'.join(result)

@app.route('/generate_prescription', methods=['POST'])
def generate_prescription():
    # Check if image is provided
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    file = request.files['image']
    img = Image.open(file.stream)  # Open image using PIL

    # Generate prescription using Gemini API
    try:
        response = model.generate_content([
            "Write information in pointer format, ordered by name of medicine, symptoms, primary diagnosis, usage, and dosage of the medicine in the image. Make sure to ask person to visit doctor if problem presists.",
            img
        ])
        formatted_response = to_plain_text(response.text)
        return jsonify({'prescription': formatted_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
