from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from genoms import (eye_colors, hair_colors, skin_colors, hair_textures, heights,
                   facial_structures, age_appearances, nose_types, lip_shapes, body_types)
from image_generator import generate
from dotenv import load_dotenv

# API Key from environment variable


load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/analyze-dna": {"origins": "http://localhost:5000"}})
API_KEY = os.getenv("API_KEY")
def analyze_dna(user_dna):
    url = "https://api.perplexity.ai/chat/completions"
    if len(user_dna) != 40 or not all(base in "ATCG" for base in user_dna):
        return "Error: Sequence must be 40 characters long and contain only A, T, C, G."

    # Split into 10 parts of 4 characters each
    parts = [user_dna[i:i+4] for i in range(0, 40, 4)]

    # Mapping dictionaries to traits
    trait_mappings = [
        (eye_colors, "Eye color"),
        (hair_colors, "Hair color"),
        (skin_colors, "Skin color"),
        (hair_textures, "Hair texture"),
        (heights, "Height"),
        (facial_structures, "Facial structure"),
        (age_appearances, "Age appearance"),
        (nose_types, "Nose Types"),
        (lip_shapes, "Lip shape"),
        (body_types, "Body type")
    ]

    # Analyze each part against the mappings
    analysis_result = {}
    for i, (mapping, trait_name) in enumerate(trait_mappings):
        segment = parts[i]
        # Check if the segment matches a predefined pattern
        matched_trait = next((trait for trait, pattern in mapping.items() if pattern == segment), "Unknown")
        analysis_result[trait_name] = matched_trait

    prompt = f"""
    You are a DNA analysis assistant. You will compare and analyze the userDNA with predefined patterns and you will generate text appearance of that userDNA.
    The sequence is 40 characters long and contains only the letters A, T, C, and G.
    Given the DNA sequence {user_dna} divided into 10 parts of 4 characters each:
    1. Eye color: {parts[0]} ({analysis_result['Eye color']})
    2. Hair color: {parts[1]} ({analysis_result['Hair color']})
    3. Skin color: {parts[2]} ({analysis_result['Skin color']})
    4. Hair texture: {parts[3]} ({analysis_result['Hair texture']})
    5. Height: {parts[4]} ({analysis_result['Height']})
    6. Facial structure: {parts[5]} ({analysis_result['Facial structure']})
    7. Age appearance: {parts[6]} ({analysis_result['Age appearance']})
    8. Nose Types: {parts[7]} ({analysis_result['Nose Types']})
    9. Lip shape: {parts[8]} ({analysis_result['Lip shape']})
    10. Body type: {parts[9]} ({analysis_result['Body type']})

    Provide a concise, creative description of the person's appearance based on these traits.
    Format the output as:
    This person stands out with [description] eyes. Their [description] hair is [description] and shines brightly.
    They have smooth [description] skin that matches their [description] height.
    Their [description] shape makes them look neat and stylish.
    We know their [description] facial structure, [description] age appearance, 
    or [description] facial features, including [description] lip shape, but their overall appearance is enhanced by their colors and hair.
    """

    # Payload for the API request
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.8,
    }

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"

    }

    # Check if the API key is available
    if not API_KEY:
        print("Error: API key not found. Please set the SONAR_API_KEY environment variable.")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                description = data['choices'][0]['message']['content']
                image_path = generate(description)  # Call the image generation function
                generated_image = generate(description)  # Removed output_file argument
                if not generated_image:
                    return {"error": "Failed to generate image."}
                return {
                    "description": description,
                    "image_url": generated_image
                }
            return {"error": "No valid response from Sonar API."}
        return {"error": f"API request failed with status {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Sonar request error: {str(e)}"}

def validate_dna(sequence):
    clean_sequence = sequence.upper().replace(" ", "").strip()
    return clean_sequence if len(clean_sequence) == 40 and all(base in "ATCG" for base in clean_sequence) else None

@app.route("/analyze-dna", methods=["POST"])
def analyze_dna_route():
    data = request.get_json()
    sequence = data.get("sequence", "")
    cleaned_sequence = validate_dna(sequence)
    if not cleaned_sequence:
        return jsonify({"error": "Invalid DNA sequence! Must be 40 characters long and contain only A, T, C, G."}), 400

    result = analyze_dna(cleaned_sequence)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)