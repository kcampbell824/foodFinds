import os
import re
import requests
from dotenv import find_dotenv, load_dotenv

# SPOONACULAR_API_KEY_NAME = "SPOONACULAR_API_KEY"
apiKey = os.getenv("API_KEY")


# The root endpoint URL for all Spoonacular API calls.
url = "https://api.spoonacular.com/"


def get_recipe_summary(id):
    params = {"apiKey": apiKey}
    headers = {}
    data = {}
    baseurl = url + f"recipes/{id}/summary"
    res = requests.get(
        url=baseurl, headers={"Content-Type": "application/json"}, params=params
    )
    data = res.json()
    sum = data["summary"]
    clean_string = re.compile("<.*?>")
    summary = re.sub(clean_string, "", str(sum))
    return summary


def get_recipe(query, intolerance):
    params = {"apiKey": apiKey}
    headers = {}
    data = {}
    # query = "pasta"
    # print(query)
    params["query"] = query
    # params["cuisine"] = cuisine
    params["intolerances"] = intolerance
    baseurl = url + "recipes/complexSearch"
    #  + "?apiKey=" + apiKey
    res = requests.get(url=baseurl, headers=headers, params=params)
    data = res.json()

    # total_results = data["results"]["totalReults"]
    recipes = []
    for recipe in data["results"]:
        recipes.append(
            {
                "id": recipe["id"],
                "name": recipe["title"],
                "image": recipe["image"],
                "summary": get_recipe_summary(recipe["id"]),
            }
        )
        # print(recipe)
    # print(recipes)
    return recipes
    # return data


def get_ingredient(query):
    params = {"apiKey": apiKey}
    headers = {}
    data = {}
    # query = "pasta"
    # print(query)
    params["query"] = query
    # params["cuisine"] = cuisine
    baseurl = url + "food/ingredients/search"
    #  + "?apiKey=" + apiKey
    res = requests.get(url=baseurl, headers=headers, params=params)
    data = res.json()
    # print(data)
    # total_results = data["results"]["totalReults"]
    ingredients = []
    for ingredient in data["results"]:
        ingredients.append(
            {
                "id": ingredient["id"],
                "name": ingredient["name"],
                "image": " https://spoonacular.com/cdn/ingredients_100x100/"
                + ingredient["image"],
            }
        )
    # print(recipe)
    # print(ingredient)
    return ingredients
    # return data
