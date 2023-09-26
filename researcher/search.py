import os
import sys
import time
import requests
import openai
from serpapi import GoogleSearch
from dotenv import load_dotenv
from termcolor import colored
from tqdm import tqdm
import concurrent.futures
import colorama
colorama.init(autoreset=True)
from config import Config

load_dotenv()

cfg = Config()

# Configure OpenAI API key
try:
    #openai.api_key = cfg.openai_api_key
    openai.api_key = cfg.openai_api_key_fast
    browserless_api_key = cfg.browserless_api_key
    openai_model = cfg.llm_model
    serpapi_api_key = cfg.serpapi_api_key
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)

headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
params = {'token': browserless_api_key}

def scrape(link):
    """Scrape the content of a webpage."""
    json_data = {
        'url': link,
        'elements': [{'selector': 'body'}],
    }
    response = requests.post('https://chrome.browserless.io/scrape', params=params, headers=headers, json=json_data)

    if response.status_code == 200:
        webpage_text = response.json()['data'][0]['results'][0]['text']
        return webpage_text
    else:
        return ""

def summarize(question, webpage_text):
    """Summarize the relevant information from a body of text related to a question."""
    prompt = f"""You are an intelligent summarization engine. Extract and summarize the
  most relevant information from a body of text related to a question.

  Question: {question}

  Body of text to extract and summarize information from:
  {webpage_text[0:2500]}

  Relevant information:"""

    while True:
        try:
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Sleeping for 3 seconds.")
            time.sleep(3)
        except openai.error.ServiceUnavailableError:
            print("Service unavailable. Retrying in 5 seconds.")
            time.sleep(5)

def final_summary(question, summaries):
    """Construct a final summary from a list of summaries."""
    num_summaries = len(summaries)
    prompt = f"You are an intelligent summarization engine. Extract and summarize relevant information from the {num_summaries} points below to construct an answer to a question.\n\nQuestion: {question}\n\nRelevant Information:"

    for i, summary in enumerate(summaries):
        prompt += f"\n{i + 1}. {summary}"

    while True:
        try:
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Sleeping for 3 seconds.")
            time.sleep(3)
        except openai.error.ServiceUnavailableError:
            print("Service unavailable. Retrying in 5 seconds.")
            time.sleep(5)

def link(r):
    """Extract the link from a search result."""
    return r['link']

def search_results(question):
    """Get search results for a question."""
    search = GoogleSearch({
        "q": question,
        "api_key": serpapi_api_key,
        "logging": False
    })

    result = search.get_dict()
    return list(map(link, result['organic_results']))

def print_citations(links, summaries):
    """Print citations for the summaries."""
    print("CITATIONS")
    num_citations = min(len(links), len(summaries))
    for i in range(num_citations):
        print(f"[{i + 1}] {links[i]}\n{summaries[i]}\n")

def scrape_and_summarize(link, question):
    """Scrape the content of a webpage and summarize it."""
    webpage_text = scrape(link)
    summary = summarize(question, webpage_text)
    return summary

def go(keyphrase=None):
    if keyphrase is None:
        keyphrase = input("What would you like me to search?")
    links = search_results(keyphrase)[:7]  # Limit the number of search results
    summaries = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_summary = {executor.submit(scrape_and_summarize, link, keyphrase): link for link in links}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_summary)):
            summaries.append(future.result())
            print(f"Step {i+1}: Scraping and summarizing link {i+1}")

    print("Step 9: Generating final summary")
    answer = final_summary(keyphrase, summaries)

    #print("HERE IS THE ANSWER")
    #print(answer)
    #print_citations(links, summaries)
    return answer

if __name__ == "__main__":
    go()