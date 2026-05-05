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
map_file = os.path.join(data_folder, "url_map.json") # File name for the URL to filename mapping/ To also make sure the json file is the data_folder

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


def save_page(response, output_dir, page_count):
    filename = os.path.join(output_dir, f"page_{page_count}.html")
    with open(filename, "wb") as f:
        f.write(response.body)

def seed_folder_store(seed_url, output_dir):
    folder_name = seed_url

    # remove protocol
    folder_name = folder_name.replace("https://", "")
    folder_name = folder_name.replace("http://", "")

    # clean invalid characters
    invalids = ['.', '/', ':', '?', '&', '=', '%', '#', '!', '@']
    for char in invalids:
        folder_name = folder_name.replace(char, "_")

    # remove duplicate underscores
    while "__" in folder_name:
        folder_name = folder_name.replace("__", "_")

    folder_name = folder_name.strip("_")

    # limit length
    folder_name = folder_name[:40]

    # create inside output_dir (IMPORTANT FIX)
    new_dir = os.path.join(output_dir, folder_name)
    os.makedirs(new_dir, exist_ok=True)

    print(f"Created folder: {new_dir}")
    return new_dir