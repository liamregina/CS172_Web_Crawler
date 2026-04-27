import os
import hashlib # Need it for the md5 hash function
import json # For saving the metadata
'''
# Starter Code (simple HTML storage function)

def save_page(url, html_content):
    os.makedirs("data", exist_ok=True) # This will create a folder name "data"

    filename = url.replace("https://", "").replace("http://", "").replace("/", "_") # Convert URL to a filename
    filepath = os.path.join("data", filename + ".html") # Created a file path for the HTML file

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Saved: {filepath}") 
'''
data_folder = "data" # Folder name
map_file = "url_map.json" # File name for the URL to filename mapping

# Just giving the url a unique id (hash)
def url_filename_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

# Checking if json file exists, if not create an empty dictionary
def load_map():
    if not os.path.exists(map_file):
        return {}
    
    with open(map_file, "r") as f: # But if map_file exists, open/load the mapping from the json file as a python dictionary
        return json.load(f)

# This is to keep updating the mapped dictionary and sending it to the Json file (updated)
def save_map(mapping):
    with open(map_file, "w") as f:
        json.dump(mapping, f, indent=2)

def save_page(url, html_content):
    pass

