"""
THIS FILE IS FOR HELPER FUNCTIONS THAT CALL SPOONACULAR AND RETURN DATA
"""
from configparser import ConfigParser
import requests

config = ConfigParser()
config.read('config/keys_config.cfg')
API_KEY = config.get('spoonacular', 'api_key')
ComplexSearchURL = ('https://api.spoonacular.com/recipes/complexSearch?apiKey={}&{}')
RandomSearchURL = ('https://api.spoonacular.com/recipes/random?apiKey={}&number={}')

def RandomRecipe(count, nutrition=False):
  try:
    str = RandomSearchURL
    if nutrition:
      str = str + "&includeNutrition=true"
    data = requests.get(str.format(API_KEY, count)).json()
    print(data)
  except Exception as exc:
    print(exc)
    data = None
  return data