# AIBlogPilotGPT

Auto blogging/article writing tool including image generation from Midjourney and publishing to Wordpress (Gutenberg ready).

Research of internet included to get most relevant articles.

The length of articles is 4000 to 8000 words (can be updated via structure of article).

## What you need for AIBlogPilot to run

- OpenAI API key
- SerpAPI key
- Browserless API Key
- TNL Api Key (https://www.thenextleg.io/) for Midjourney Image Generation

## Steps

Install requirements via pip install -r requirements.txt

Include all API keys to example.env and rename it to .env.

Include your Wordpress details to .env. If you want to include more blogs, you cann add as WP_ADMIN_USERNAME_2, WP_ADMIN_USERNAME_3 etc. The numbering goes for all details.

Go to blogs/blogs.toml and include all details about your blog. In terms of keywords, I suggest you change them with every run.

For a single article, go to main.py and uncomment line 319 (article()) and comment line 320 (parse_blog_articles())

For multiple articles, go to main.py and comment line 319 (article()) and uncomment line 320 (parse_blog_articles())

The default generation is 15 articles. If you want to change it, go to orchestrar/blogs.py and change the prompt in init_blog function ("I want you to propose next 15 article titles")

All articles and images are saved temp directory.

