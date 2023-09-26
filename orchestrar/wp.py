import xmlrpc.client as xmlrpc_client
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from dotenv import load_dotenv
from config import Config
import requests
import json

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Load the .env file
load_dotenv()

# Configure OpenAI API key
cfg = Config()


def get_all_articles(site_url):
    page = 1
    published_articles = ""
    while True:
        response = requests.get(f'{site_url}/wp-json/wp/v2/posts?page={page}')
        posts = json.loads(response.text)

        # Check if posts is a list
        if not isinstance(posts, list):
            break

        if len(posts) == 0:
            break

        for post in posts:
            # Check if the post is a dictionary
            if not isinstance(post, dict):
                continue

            #published_articles += post['title']['rendered'] + '\n' + post['content']['rendered'] + ', \n\n'
            published_articles += 'Article ID: ' + str(post['id']) + '\nwith Article Title: ' + post['title']['rendered'] + '\nand Article Content: ' + post['content']['rendered'] + ', \n\n'
            #print(post['title']['rendered'])

        page += 1

    return published_articles



def get_all_posts_titles(site_url):
    page = 1
    published_articles = ""
    while True:
        response = requests.get(f'{site_url}/wp-json/wp/v2/posts?page={page}')
        posts = json.loads(response.text)

        # Check if posts is a list
        if not isinstance(posts, list):
            break

        if len(posts) == 0:
            break

        for post in posts:
            # Check if the post is a dictionary
            if not isinstance(post, dict):
                continue

            published_articles += post['title']['rendered'] + ', '
            #print(post['title']['rendered'])

        page += 1

    return published_articles

# Example usage:
#site_url = 'https://iminsweden.com/'
#get_all_posts_titles(site_url)

def post_to_wordpress(title, content, category, tags, image_path=None, wp_admin=None, wp_password=None, wp_url=None):
    wp_url = wp_url if wp_url is not None else cfg.site_url
    wp_username = wp_admin if wp_admin is not None else cfg.wp_admin_username
    wp_password = wp_password if wp_password is not None else cfg.wp_admin_password

    wp = Client(wp_url, wp_username, wp_password)

    post = WordPressPost()
    post.title = title
    post.content = content
    post.terms_names = {
        'category': [category],
        'post_tag': tags
    }
    post.post_status = 'publish'  # Set the status of the new post.

    # If an image path is provided, upload the image and set it as the featured image
    if image_path is not None:
        data = {
            'name': 'picture.jpg',
            'type': 'image/jpeg',  # mimetype
        }

        # read the binary file and let the XMLRPC library encode it into base64
        with open(image_path, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())

        response = wp.call(UploadFile(data))
        attachment_id = response['id']

        post.thumbnail = attachment_id

    wp.call(NewPost(post))

def load_post_from_wp():
    return 0


if __name__ == "__main__":
    post_to_wordpress("aaaa", "Uncategorized", "Uncategorized", "", "../temp/imgs/C1CH8g2L7m102KkTG8tI_small.jpg")