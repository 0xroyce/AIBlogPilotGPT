import os
import sys
import json
from dotenv import load_dotenv
import openai
import toml
from halo import Halo
import colorama
from termcolor import colored
import time
from colorama import Fore, Style
colorama.init(autoreset=True)
from pyfiglet import Figlet

from config import Config

from initiation import kickoff
import articles.writing
from articles import skeleton
from articles import writing
from researcher import search
from orchestrar import gutenberg
from orchestrar import wp
from orchestrar import blogs
from enhancer import midjourney_ai

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize colorama
colorama.init(autoreset=True)

# Load the .env file
load_dotenv()

# Configure OpenAI API key
cfg = Config()
try:
    openai.api_key = cfg.openai_api_key
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)

# Global variables for article content
article_content = ""
article_title = ""
article_description = ""
findings = ""
wp_admin = ""
wp_pass = ""
wp_url = ""
published_articles = ""
tone = ""
keywords = ""

def process_section(section, level=2, max_depth=5):
    """
    Process a section or subsection of the article.
    """
    section_type = 'section' if level == 2 else 'subsection'
    section_content = ""
    spinner = Halo(text=f'Processing {section_type}: {section[f"Heading_H{level}"]}', spinner='dots')
    spinner.start()

    # Write section or subsection
    section_content = articles.writing.write_section(article_title,
                                                     article_description,
                                                     section[f'Heading_H{level}'],
                                                     section['Description'],
                                                     tone)

    spinner.succeed(f"Finished processing {section_type}: {section[f'Heading_H{level}']}")

    # Process subsections if they exist and the maximum depth has not been reached
    if 'SubSections' in section and level < max_depth:
        for sub_section in section['SubSections']:
            section_content += process_section(sub_section, level + 1)

    return "\n\n" + f"<h{level}>" + section[f'Heading_H{level}'] + f"</h{level}>" + "\n\n" + section_content


def process_json(json_string):
    """
    Process the JSON string to generate the article content.
    """
    global article_content
    global article_title  # Declare article_title as global
    spinner = Halo(text='Parsing JSON', spinner='dots')
    spinner.start()

    data = json.loads(json_string)
    article_title = data['Title']  # This now refers to the global variable
    if findings.strip():
        article_description = data['Description'] + " " +f"""{findings}"""
        #print("\n\n\n\nArticle_description: ", article_description)
        #print("\n\n\n\n")
    else:
        article_description = data['Description']

    spinner.succeed('Finished parsing JSON')

    # Add the intro to the article content
    article_content += writing.write_intro(article_title, tone) + "\n\n"

    for section in data['Sections']:
        article_content += process_section(section)

    return article_content

def is_json(json_string):
    """
    Check if a string is valid JSON.
    """
    try:
        json.loads(json_string)
    except ValueError:
        return False
    return True

def wait_for_image(image_name):
    """
    Function to wait for the image file to appear in the specified directory
    """
    # Define the base directory
    base_dir = "./temp/imgs/"

    # Use os.path.join to create the full path
    image_path = os.path.join(base_dir, image_name)
    print(f"Looking for image at: {image_path}")

    # Keep checking for the image file until it appears
    while True:
        try:
            if os.path.isfile(image_path):
                print("Image file found.")
                break
            else:
                print("Image file not found. Waiting...")
                time.sleep(5)  # wait for 5 seconds before checking again
        except Exception as e:
            print(f"Error while checking for image: {e}")
            break


def article(title=None, category=None):
    """
    Main function to generate the article.
    """
    global findings
    global article_content
    global article_title

    # Reset article_content
    article_content = ""

    if title is None:
        title = input("Please enter the article title: ")
    else:
        print(f"Article Title: {title}")
    if category is None:
        category = input("Please enter the article category: ")
    else:
        print(f"Article Category: {category}")

    # RESEARCH
    if title is not None and category is not None:
        research = 'y'
    else:
        research = input("Do you want me to research the internet? (y/n): ")
    if research == 'y':
        search_results = search.go(title)
        findings = f"""This is additional info from user you need to incorporate: {search_results}"""
        print(colored("\n" + "################### RESEARCH FINISHED ###################\n", "green", attrs=["bold"]))

    # ARTICLE TYPE
    if title is not None and category is not None:
        article_type = 'a'
    else:
        article_type = input("Do you want Article or Product Review? (a/p): ")
    spinner = Halo(text='Preparing Structure of Article', spinner='dots')
    spinner.start()

    article_skeleton = ""
    while not is_json(article_skeleton):
        try:
            if article_type == 'a':
                article_skeleton = skeleton.write_skeleton(title)
            elif article_type == 'p':
                article_skeleton = skeleton.write_skeleton_product_review(title)
        except Exception as e:
            spinner.fail(str(e))
        else:
            spinner.succeed("Finished writing the article skeleton")

    # PROCESS SECTIONS
    try:
        article_content += process_json(article_skeleton)
    except Exception as e:
        spinner.fail(str(e))
    else:
        spinner.succeed("Finished processing JSON")

    print(colored("\n" + "################### ARTICLE GENERATED ###################", "green",
                  attrs=["bold"]))

    # SAVE TO TXT FILE
    if title is not None and category is not None:
        save_to_txt = 'y'
    else:
        save_to_txt = input("Do you want to save this article to a txt file? (y/n): ")
    if save_to_txt == 'y':
        with open(f"./temp/articles/{title}.txt", "w") as file:
            file.write(article_content)
        print(colored("\nArticle saved to txt file.", "green", attrs=["bold"]))

    # GENERATE IMAGES
    featured_image_name = midjourney_ai.generate_image(title)

    # Wait for the image file to appear
    wait_for_image(featured_image_name + "_small.jpg")

    # Define the base directory
    base_dir = "/temp/imgs"

    # Use os.path.join to create the full path
    featured_image_path = os.path.join(base_dir, featured_image_name + "_small.jpg")
    featured_image_path = "." + featured_image_path

    # WORDPRESS IMPORT
    if title is not None and category is not None:
        wp_import = 'y'
    else:
        wp_import = input("Do you want to import this article to WordPress? (y/n): ")
    if wp_import == 'y':
        print(colored("\n" + "################### WORDPRESS IMPORT ###################", "green",
                      attrs=["bold"]))

        spinner = Halo(text='Preparing article for WordPress import', spinner='dots')
        spinner.start()
        try:
            to_wordpress = gutenberg.convert_to_gutenberg_blocks(article_content)
            tags = [category]
            wp.post_to_wordpress(article_title, to_wordpress, category, tags, featured_image_path, wp_admin, wp_pass, wp_url)
        except Exception as e:
            spinner.fail(str(e))
        else:
            spinner.succeed("Article imported to WordPress\n\n")

def parse_blog_articles():
    data = json.loads(get_blog_details())

    for item in data:
        #print(f'Category: {item["Category"]}, Title: {item["Title"]}')
        article(item["Title"], item["Category"])

def get_blog_details():
    global wp_admin
    global wp_pass
    global wp_url
    global tone
    global keywords

    data = toml.load("blogs/blogs.toml")

    # print all the blogs and ask user to choose one
    print("List of blogs:")
    for i, blog in enumerate(data["blog"], start=1):
        print(f"{i}. {blog['name']}")

    # ask user for blog number
    blog_number = int(input("\nEnter the number of the blog: "))
    # get the chosen blog
    chosen_blog = data["blog"][blog_number - 1]

    # get the WP admin username and password from the .env file
    wp_admin = os.getenv(f"WP_ADMIN_USERNAME_{chosen_blog['id']}")
    wp_pass = os.getenv(f"WP_ADMIN_PASSWORD_{chosen_blog['id']}")
    wp_url = os.getenv(f"WP_URL_{chosen_blog['id']}")

    print(f"\nBlog Name: {chosen_blog['name']}")
    print(f"Description: {chosen_blog['description']}")
    print(f"URL: {chosen_blog['url']}")
    print(f"Tone: {chosen_blog['tone']}")
    print(f"Keywords: {chosen_blog['keywords']}")
    #print(f"WordPress Admin: {wp_admin}")
    #print(f"WordPress Password: {wp_pass}")

    print("\n")

    tone = chosen_blog['tone']
    keywords = chosen_blog['keywords']

    # get the published articles from the blog
    spinner = Halo(text='Loading existing articles...', spinner='dots')
    spinner.start()
    try:
        published_articles = wp.get_all_posts_titles(chosen_blog['url'])
    except Exception as e:
        spinner.fail(str(e))
    else:
        spinner.succeed("Articles loaded")

    # generate the JSON for the articles
    spinner = Halo(text='Generating articles JSON', spinner='dots')
    spinner.start()
    try:
        json_articles = blogs.init_blog(chosen_blog['description'],published_articles, tone, keywords)
    except Exception as e:
        spinner.fail(str(e))
    else:
        spinner.succeed("JSON Generated")

    print(json_articles)
    return json_articles

if __name__ == "__main__":
    f = Figlet(font='big', width=300)
    print(Fore.CYAN + Style.BRIGHT + f.renderText('AI BLOG PILOT'))
    #article()
    parse_blog_articles()