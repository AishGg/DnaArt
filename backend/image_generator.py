import base64
import os
import mimetypes
import glob  # Add this import for file deletion
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()


def generate(user_description):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""want to generate a image of person by giving a description about his/her appearance"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Great! I'm ready to help you visualize that person. To generate the best possible image, please provide as much detail as you can about their appearance. Consider including information in these categories:

                    **General Information:**

                    *   **Gender:** Male, female, non-binary, etc.
                    *   **Age:** Child, teenager, young adult, middle-aged, elderly, or a specific age range.
                    *   **Ethnicity/Race:** Be as specific or general as you like (e.g., Caucasian, African, Asian, Hispanic, etc.).
                    *   **Overall Impression:** What is the first feeling or adjective that comes to mind when you imagine this person (e.g., kind, stern, mysterious, cheerful, sophisticated, rugged)?

                    **Facial Features:**

                    *   **Face Shape:** Round, oval, square, heart-shaped, long, etc.
                    *   **Hair:**
                        *   **Color:** (e.g., brown, black, blonde, red, grey, white, vibrant colors)
                        *   **Length:** (e.g., short, medium, long)
                        *   **Style:** (e.g., straight, wavy, curly, frizzy, bald, shaved, ponytail, bun, braids, dreadlocks, specific haircut like a pixie or bob)
                        *   **Texture:** (e.g., thick, thin, fine, coarse)
                    *   **Eyes:**
                        *   **Color:** (e.g., blue, green, brown, hazel, grey)
                        *   **Shape:** (e.g., almond, round, hooded, upturned, downturned)
                        *   **Size:** (e.g., large, small)
                        *   **Expression:** (e.g., piercing, gentle, thoughtful, intense)
                    *   **Eyebrows:**
                        *   **Shape:** (e.g., arched, straight, thick, thin)
                        *   **Color:**
                    *   **Nose:**
                        *   **Shape:** (e.g., straight, hooked, upturned, wide, narrow)
                        *   **Size:**
                    *   **Mouth:**
                        *   **Lip Shape:** (e.g., full, thin, heart-shaped)
                        *   **Lip Size:**
                        *   **Expression:** (e.g., smiling, neutral, frowning)
                    *   **Ears:** (mention if they are prominent, small, or have any notable features)
                    *   **Other Facial Features:** (e.g., freckles, moles, wrinkles, scars, dimples)
                    *   **Facial Hair (if applicable):** (e.g., beard, mustache, goatee, stubble - describe the style and length)

                    **Body Features:**

                    *   **Build:** (e.g., slim, athletic, muscular, stocky, slender, plus-size)
                    *   **Height:** (e.g., tall, average, short)
                    *   **Posture:** (e.g., upright, slouching)
                    *   **Skin Tone:** (e.g., fair, light, medium, tan, deep, specific undertones)

                    **Clothing and Accessories:**

                    *   **Style of Clothing:** (e.g., casual, formal, business, vintage, bohemian, sporty, specific subcultures)
                    *   **Specific Items of Clothing:** (e.g., t-shirt, jeans, dress, suit, hat, scarf, jacket)
                    *   **Colors of Clothing:**
                    *   **Accessories:** (e.g., glasses, jewelry, piercings, tattoos, bags)

                    **Pose and Setting (Optional but helpful):**

                    *   **Pose:** (e.g., standing, sitting, walking, looking directly at the viewer, looking away)
                    *   **Setting/Background:** (if you have a specific background in mind, it can influence the overall feel)

                    The more details you provide, the more accurately I can generate the image you envision. I'm excited to see who you describe!"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_description),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.85,
        response_modalities=[
            "image",
            "text",
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".bin"
            file_name = f"static/dna_image{file_extension}"  
            
            
            existing_images = sorted(glob.glob("static/*"))
            if existing_images:
                os.remove(existing_images[0])
            
            save_binary_file(file_name, inline_data.data)
            print(
                f"File of mime type {inline_data.mime_type} saved to: {file_name}"
            )
            return file_name 
        else:
            print(chunk.text)
    return None 

