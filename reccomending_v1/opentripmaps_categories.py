import json
import requests


def get_categories():
    categories_url = "https://opentripmap.io/catalog.en.json"

    response = requests.get(categories_url)

    catalog = json.loads(response.text)
    categories = []

    def dfs(node: dict):
        if 'id' in node:
            categories.append(node.get('id'))
        if 'children' in node:
            for child in node.get('children'):
                dfs(child)

    dfs(catalog)
    return categories
