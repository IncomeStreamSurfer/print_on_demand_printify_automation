import os
import openai
import pandas as pd
from tqdm import tqdm
from PIL import Image
import requests
import io
from PIL import Image, ImageDraw


# Set OpenAI and Stability.ai API keys https://platform.openai.com/account/api-keys AND https://beta.dreamstudio.ai/account
openai.api_key = 'YOUR_OPEN_AI_KEY'
stability_ai_key = 'YOUR_STABILITY_AI_KEY'

# Function to generate a clickable title using GPT-3.5-turbo 

# Change this prompt if you are changing the product type, right now it's Acrylic Wall Art Panels

def generate_clickable_title(detail):
    print("Generating clickable title...")
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
    print("Clickable title generated...")
    return clickable_title

# Function to generate a description
def generate_description(detail):
    print("Generating description...")
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

    # Append the predefined paragraph to the generated description
    description += """
    <p>Acrylic art panels are a modern way to display beautiful and vibrant art that looks like it's embedded in clear glass. They have a clear, glossy acrylic surface and a white vinyl backing. Four silver stand-offs make it very easy to mount to the wall. Make your own original designs and print them on any (or all) of the seven available panel sizes in horizontal and vertical orientations. Square dimensions are available.</p>
<p>.: Material: Clear acrylic with white vinyl backing<br />.: Clear, glossy surface<br />.: Seven sizes to choose from<br />.: Horizontal, vertical and square options available<br />.: NB! For indoor use only</p>
    """
    print("Description generated...")
    return description


# Function to generate an image prompt
def generate_image_prompt(detail):
    print("Generating image prompt...")
    prompt = f"Generate a creative prompt for an image for a T-shirt with the theme: '{detail}'. Maximum 75 characters."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    image_prompt = response['choices'][0]['message']['content'].strip()
    image_prompt = image_prompt.replace('"', '')  # Remove double quotes
    print("Image prompt generated...")
    return image_prompt

# Function to generate tags
def generate_tags(detail):
    print("Generating tags...")
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
    print("Tags generated...")
    return tag

# Load the input CSV file
csv_path = "input.csv"  
df = pd.read_csv(csv_path)

# Initialize empty lists for the new columns
file_names = []
local_paths = []
titles = []
descriptions = []
tags = []

# Loop over the rows in the DataFrame to generate the title, description, prompt, and tags
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    detail = row['details']

    # Generate the title, description, prompt, and tags using the OpenAI API
    title = generate_clickable_title(detail)
    description = generate_description(detail)
    image_prompt = generate_image_prompt(detail)
    tag = generate_tags(detail)

    

    # Generate the image using the Stability.ai API
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-beta-v2-2-2/text-to-image"
    headers = {"Authorization": f"Bearer {stability_ai_key}", "Accept": "image/png"}
    data = {
        "width": 512,
        "height": 512,
        "text_prompts": [
            {
                "text": image_prompt,
                "weight": 0.5
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    file_name = f"image_{idx}.png"  
    local_path = f"{file_name}"  # Save the image in the same directory
    image.save(local_path)

    # Append the generated data to the lists
    file_names.append(file_name)
    local_paths.append(local_path)
    titles.append(title)
    descriptions.append(description)
    tags.append(tag)

# Create a new DataFrame with the generated data
output_df = pd.DataFrame({
    "file_name": file_names,
    "local_path": local_paths,
    "title": titles,
    "description": descriptions,
    "tags": tags
})

# Save the DataFrame to a new CSV file
output_df.to_csv("product_information.csv", index=False)
