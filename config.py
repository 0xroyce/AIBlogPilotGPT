# Importing necessary libraries
import os
import openai
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

# Singleton class to ensure only one instance of a class exists
class Singleton(type):
    # Dictionary to store instances of classes
    _instances = {}

    # Overriding the __call__ method to control class instantiation
    def __call__(cls, *args, **kwargs):
        # If an instance of the class does not exist, create one
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(
                *args, **kwargs)
        # Return the instance of the class
        return cls._instances[cls]

# Config class to manage configuration settings
class Config(metaclass=Singleton):
    # Initialization method
    def __init__(self):
        # Fetching environment variables and setting them as class attributes
        self.llm_model = os.getenv("LLM_MODEL")
        self.fast_llm_model = os.getenv("FAST_LLM_MODEL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_key_fast = os.getenv("OPENAI_API_KEY_FAST")
        openai.api_key = self.openai_api_key
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        self.browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
        self.brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.wolfram_alpha_appid = os.getenv("WOLFRAM_ALPHA_APPID")
        self.site_url = os.getenv("SITE_URL")
        self.wp_admin_username = os.getenv("WP_ADMIN_USERNAME")
        self.wp_admin_password = os.getenv("WP_ADMIN_PASSWORD")

    # Method to set the llm_model attribute
    def set_llm_model(self, value: str):
        self.llm_model = value

    # Method to set the llm_model attribute
    def set_fast_llm_model(self, value: str):
        self.fast_llm_model = value

    # Method to set the openai_api_key attribute
    def set_openai_api_key(self, value: str):
        self.openai_api_key = value

    def set_openai_api_key_fast(self, value: str):
        self.openai_api_key_fast = value

    # Method to set the serp_api_key attribute
    def set_serpapi_api_key(self, value: str):
        self.serpapi_api_key = value

    # Method to set the browserless_api_key attribute
    def set_browserless_api_key(self, value: str):
        self.browserless_api_key = value

    # Method to set the brave_search_api_key attribute
    def set_brave_search_api_key(self, value: str):
        self.brave_search_api_key = value

    def set_site_url(self, value: str):
        self.site_url = value

    def set_wp_admin_username(self, value: str):
        self.wp_admin_username = value

    def set_wp_admin_password(self, value: str):
        self.wp_admin_password = value