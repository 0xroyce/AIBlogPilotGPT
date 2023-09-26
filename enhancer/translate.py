import os
import sys
import time
import requests
import openai
from serpapi import GoogleSearch
from dotenv import load_dotenv
from termcolor import colored
from tqdm import tqdm
import colorama
colorama.init(autoreset=True)
from config import Config

load_dotenv()

cfg = Config()

# Configure OpenAI API key
try:
    openai.api_key = cfg.openai_api_key
    browserless_api_key = cfg.browserless_api_key
    llm_model = cfg.llm_model
    fast_llm_model = cfg.fast_llm_model
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)



def translate_content(article, language):
    prompt = f"""Please translate the following English article into the specified language. 
            Make sure it's SEO optimised and grammatically correct.
            Language: {language}
            English Article: {article}"""

    chunked_output = ""
    for chunk in openai.ChatCompletion.create(
            model=cfg.llm_model,
            temperature=1,
            stream=True,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'system', 'content': "You're an expert translating from English to any language."},
                {'role': 'system', 'content': 'You use engaging tone of voice.'},
                {"role": "user", "content": prompt}
            ]
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            # print(content, end='')
            chunked_output += content

    return chunked_output