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
    # Making sure the data folder exists
    os.makedirs(data_folder, exist_ok=True)

    if not os.path.exists(map_file):
        return {}
    
    try:
        with open(map_file, "r") as f:
            return json.load(f)
    except:
        return {}


# This is to keep updating the mapped dictionary and sending it to the Json file (updated)
def save_map(mapping):
    with open(map_file, "w") as f:
        json.dump(mapping, f, indent=2)


def save_page(url, html_content):
    # Data folder creation
    os.makedirs(data_folder, exist_ok= True) # Creating the data folder if it doesnt exist yet
    mapping = load_map() #Loading the mapping from the json file (if it exists) as a python dictionarty

    # Duplicate check
    if url in mapping:
        print(f"Skipped (duplicate): {url}") # If the url is already in the mapping, skip saving and print a message
        return
    
    # File creation
    filename = url_filename_hash(url) + ".html" #Creating a unique filename for the HTML file
    filepath = os.path.join(data_folder, filename) 
    with open (filepath, "w", encoding="utf-8") as f:
        f.write(html_content) # Saving the HTML content to the file

    # Mapping update
    mapping[url] = filename # Here I create a mapping of the url to the filename in the mapping director (updating the directory)
    save_map(mapping) # Saving the updated mapping to the json file
    print(f"Saved: {filepath}")



