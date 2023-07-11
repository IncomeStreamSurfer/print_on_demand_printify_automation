import os
import openai
import pandas as pd
from tqdm import tqdm
from PIL import Image
import requests
import io

# Set OpenAI and Stability.ai API keys
openai.api_key = 'YOUR_OPEN_AI_KEY'
stability_ai_key = 'YOUR_STABILITY_AI_KEY'

# Set Stability API key for image upscaling
api_key = 'YOUR_STABILITY_AI_KEY'
if api_key is None:
    raise Exception("Missing Stability API key.")
api_host = os.getenv("API_HOST", "https://api.stability.ai")


def generate_clickable_title(detail):
    prompt = f"Generate a catchy and clickable title for a T-shirt with the theme: '{detail}'. Maximum 50 characters. At the end of each title write Acrylic Wall Art Panels"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    clickable_title = response['choices'][0]['message']['content'].strip()
    clickable_title = clickable_title.replace('"', '')  # Remove double quotes
    return clickable_title

def generate_description(detail):
    prompt = f"Generate a compelling description for a T-shirt with the theme: '{detail}'. Maximum 150 characters."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    description = response['choices'][0]['message']['content'].strip()
    description = description.replace('"', '')  # Remove double quotes
    description += """
    <p>Acrylic art panels are a modern way to display beautiful and vibrant art that looks like it's embedded in clear glass. They have a clear, glossy acrylic surface and a white vinyl backing. Four silver stand-offs make it very easy to mount to the wall. Make your own original designs and print them on any (or all) of the seven available panel sizes in horizontal and vertical orientations. Square dimensions are available.</p>
<p>.: Material: Clear acrylic with white vinyl backing<br />.: Clear, glossy surface<br />.: Seven sizes to choose from<br />.: Horizontal, vertical and square options available<br />.: NB! For indoor use only</p>
    """
    return description

def generate_tags(detail):
    prompt = f"Generate relevant tags for a T-shirt with the theme: '{detail}'. Separate the tags with commas."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    tag = response['choices'][0]['message']['content'].strip()
    tag = tag.replace('"', '')  # Remove double quotes
    return tag

csv_path = "input.csv"  
df = pd.read_csv(csv_path)

file_names = []
local_paths = []
titles = []
descriptions = []
tags = []

for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    detail = row['details']
    title = generate_clickable_title(detail)
    description = generate_description(detail)
    tag = generate_tags(detail)

    # Use the detail from the CSV as the image prompt
    image_prompt = detail

    # Generate the image using stable diffusion
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image"
    headers = {"Authorization": f"Bearer {stability_ai_key}", "Accept": "image/png"}
    data = {
        "width": 512,
        "height": 512,
        "text_prompts": [
            {
                "text": image_prompt,
                "weight": 0.5,
            
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    file_name = f"image_{idx}.png"  
    local_path = f"{file_name}"  
    image.save(local_path)

    # Upscale the image using the "esrgan-v1-x2plus" engine
    response = requests.post(
        f"{api_host}/v1/generation/esrgan-v1-x2plus/image-to-image/upscale",
        headers={
            "Accept": "image/png",
            "Authorization": f"Bearer {api_key}"
        },
        files={
            "image": open(local_path, "rb")
        },
        data={
            "width": 2048,
        }
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    upscaled_path = f"upscaled_{file_name}"
    with open(upscaled_path, "wb") as f:
        f.write(response.content)
    local_paths.append(upscaled_path)

    file_names.append(file_name)
    titles.append(title)
    descriptions.append(description)
    tags.append(tag)

output_df = pd.DataFrame({
    "file_name": file_names,
    "local_path": local_paths,
    "title": titles,
    "description": descriptions,
    "tags": tags
})

output_df.to_csv("product_information.csv", index=False)
