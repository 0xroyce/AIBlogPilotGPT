import requests
import json

def get_post_by_title(site_url, title):
    response = requests.get(f'{site_url}/wp-json/wp/v2/posts?search={title}')
    posts = json.loads(response.text)

    if len(posts) == 0:
        print("No posts found with that title.")
    else:
        for post in posts:
            print(post['title']['rendered'])
            print(post['content']['rendered'])

# Example usage:
site_url = 'https://iminsweden.com/'
title = 'A Comprehensive Overview of the Swedish Education System'
get_post_by_title(site_url, title)
