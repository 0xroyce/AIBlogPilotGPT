# Import necessary libraries
from midjourney_api import TNL
import requests
import json
import time
import os
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Define API key and initialize TNL
TNL_API_KEY = os.getenv("TNL_API_KEY")
tnl = TNL(TNL_API_KEY)


def generate_image(title):
    """
    Function to generate image using TNL API
    """
    # Define the prompt for the image
    prompt = f"""Header image for an article '{title}',extra sharp, 8k, photorealistic, shot on Kodak gold --ar 16:9"""

    # Get the response from the API
    response = tnl.imagine(prompt)

    # Keep checking until message_id is not None
    while "messageId" not in response:
        print("Waiting for message id...")
        time.sleep(5)  # wait for 5 seconds before checking again

    print("Message id: ", response["messageId"])

    # Call check_progress function to wait for the image generation to complete
    check_progress(response["messageId"])

    return response["messageId"]


def check_progress(id):
    """
    Function to check the progress of the image generation and download the image
    """
    # Define the URL and headers for the request
    url = f"https://api.thenextleg.io/v2/message/{id}?expireMins=12"
    headers = {'Authorization': f'Bearer {TNL_API_KEY}'}

    # Initialize progress bar
    progress_bar = tqdm(total=100)

    # Keep checking the progress until it reaches 100
    while True:
        response = requests.get(url, headers=headers)
        response_json = response.json()

        # Convert response_json['progress'] to an integer before subtracting progress_bar.n
        progress_bar.update(int(response_json['progress']) - progress_bar.n)  # Update progress bar

        if int(response_json['progress']) == 100:
            progress_bar.close()  # Close progress bar
            break
        else:
            time.sleep(5)

    # Get the URL of the third image
    third_image_url = response_json['response']['imageUrls'][2]

    print(third_image_url)

    # Download the image
    download_image(third_image_url, id)


def download_image(image_url, id):
    """
    Function to download the image and save it in different formats
    """
    url = "https://api.thenextleg.io/getImage"
    payload = json.dumps({"imgUrl": image_url})
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TNL_API_KEY}'
    }

    response = requests.post(url, headers=headers, data=payload)

    # Assuming the response is in bytes
    image = Image.open(BytesIO(response.content))

    # Define the directory to save the images
    directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'temp', 'imgs')

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Save the images in the defined directory
    image.save(os.path.join(directory, f'{id}.png'))

    original_image = Image.open(os.path.join(directory, f'{id}.png'))
    rgb_image = original_image.convert('RGB')
    small_image_name = f'{id}_small.jpg'
    rgb_image.save(os.path.join(directory, small_image_name), "JPEG", quality=70)

    return small_image_name


def generate_and_check(title):
    """
    Main function to generate the image and check its progress
    """
    message_id = generate_image(title)
    check_progress(message_id)


if __name__ == "__main__":
    generate_and_check("Top 5 Renewable Energy Sources for 2023")