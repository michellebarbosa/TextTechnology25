import requests
from pymongo import MongoClient
import time
from urllib.parse import quote
import pandas as pd
from bs4 import BeautifulSoup

# MongoDB setup (unchanged)
client = MongoClient('mongodb+srv://testingco:Ilovescience08@shakespear.hgzdqud.mongodb.net/?retryWrites=true&w=majority&appName=shakespear')  
db = client['dracor_db']  
plays_collection = db['plays']  
corpora_collection = db['corpora']  

# DraCor API configuration (unchanged)
API_VERSION = "v1"  
API_URL = "https://dracor.org/api/v1/"

# Your original code for getting corpus list (unchanged)
CORPORA_EXT_PLAIN = "corpora"
api_corpora_url = API_URL + CORPORA_EXT_PLAIN
print(f"URL for getting the list of corpora: {api_corpora_url}\n")
corpus_list = requests.get(api_corpora_url).json()
corpus_abbreviations = []
for corpus_description in corpus_list:
    name = corpus_description["name"]
    print(f'{name}: {corpus_description["title"]}')
    corpus_abbreviations.append(name)

# Your original corpus selection (unchanged)
CORPORA_EXT = "corpora/"
METADAT_EXT = "/metadata"
for i in range(10):
    corpusname = str(input("Please choose a corpusname from the list above. Enter the abbreviation: "))
    if corpusname not in corpus_abbreviations:
        print("The abbreviation you selected is not in the list. Please enter the abbreviation again.")
    else:
        print("Success!")
        break
else:
    corpusname = "swe"

# Your original metadata retrieval (unchanged)
corpus_metadata_path = API_URL + CORPORA_EXT + corpusname + METADAT_EXT
print(f"URL for getting the metadata of a specific corpus: {corpus_metadata_path}\n")
metadata_file = requests.get(corpus_metadata_path, headers={"accept": "text/csv"}, stream=True)
metadata_file.raw.decode_content=True
metadata_df = pd.read_csv(metadata_file.raw, sep=",", encoding="utf-8")

# Your original play selection (unchanged)
PLAY_EXT = "/plays/"
PLAY_KEY = "name"
for i in range(10):
    play_name = str(input("Please choose a text from the corpus you have chosen. Enter the text name: "))
    if play_name not in metadata_df[PLAY_KEY].values:
        print("The name you selected is not in the list. Please enter the name again.")
    else:
        print("Success!")
        break
else:
    play_name = "strindberg-gillets-hemlighet"

# Corrected TEI endpoint (minimal change)
TEI_EXT = "/tei"
play_tei_path = API_URL + CORPORA_EXT + corpusname + PLAY_EXT + play_name + TEI_EXT
print(f"URL for getting TEI of a specific play: {play_tei_path}\n")

# Get TEI data
tei_response = requests.get(play_tei_path)
tei_response.raise_for_status()  # Check for errors

# Store in MongoDB (NEW - this is what you asked about)
play_data = {
    "corpus": corpusname,
    "play_name": play_name,
    "tei_xml": tei_response.text,  # Storing raw XML
    "metadata": metadata_df[metadata_df[PLAY_KEY] == play_name].to_dict('records')[0],
    "timestamp": time.time()
}

# Insert into MongoDB
result = plays_collection.insert_one(play_data)
print(f"\nSuccessfully stored data in MongoDB with ID: {result.inserted_id}")

# Print confirmation
print("\nStored document contains:")
print(f"- Corpus: {corpusname}")
print(f"- Play: {play_name}")
print(f"- Metadata keys: {list(play_data['metadata'].keys())}")
print(f"- TEI XML size: {len(tei_response.text)} characters")

# You can still print the TEI if needed (first 500 chars)
print("\nFirst 500 characters of TEI:")
print(tei_response.text[:500] + "...")