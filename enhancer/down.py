import requests
import json
from PIL import Image
from io import BytesIO

url = "https://api.thenextleg.io/getImage"

payload = json.dumps({
    "imgUrl": "https://cdn.midjourney.com/0109b6ae-a6b0-4bbd-a89c-fd6071cc1763/0_2.png"
})
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer dffc660d-8ad0-4a13-bc91-119e27b8e4a3'
}

response = requests.request("POST", url, headers=headers, data=payload)

# Assuming the response is in bytes
image = Image.open(BytesIO(response.content))
image.save('output.png')


