import requests
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import csv
import io
import time
from urllib.parse import quote

# MongoDB Setup
client = MongoClient('mongodb+srv://michellebarbosa789:7y1FnkKc5VpvfAMs@shakespear.hgzdqud.mongodb.net/?retryWrites=true&w=majority&appName=shakespear')
db = client['dracor_db']
cooccurrence_collection = db['cooccurrence_networks']
tei_collection = db['tei_xmls']
metadata_collection = db['plays_metadata']

# DraCor API Configuration
DRACOR_API = "https://dracor.org/api/v1"
CORPUS = "shake"

def get_all_plays_in_corpus(corpus):
    """Fetch metadata for all plays in a corpus"""
    url = f"{DRACOR_API}/corpora/{quote(corpus)}/plays"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching plays for corpus {corpus}: {e}")
        return None

def download_cooccurrence_csv(corpus, play_name):
    """Download co-occurrence network CSV"""
    url = f"{DRACOR_API}/corpora/{quote(corpus)}/play/{quote(play_name)}/networkdata/csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading CSV for {play_name}: {e}")
        return None

def download_tei_xml(corpus, play_name):
    """Download TEI XML"""
    url = f"{DRACOR_API}/corpora/{quote(corpus)}/play/{quote(play_name)}/tei"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading TEI for {play_name}: {e}")
        return None

def store_play_data(corpus, play_metadata, csv_data, tei_data):
    """Store all data for a play in MongoDB"""
    # Store metadata
    play_metadata['corpus'] = corpus
    metadata_collection.update_one(
        {'name': play_metadata['name'], 'corpus': corpus},
        {'$set': play_metadata},
        upsert=True
    )
    
    # Store co-occurrence network (CSV)
    if csv_data:
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        cooccurrence_data = [row for row in csv_reader]
        
        cooccurrence_collection.update_one(
            {'play_name': play_metadata['name'], 'corpus': corpus},
            {'$set': {
                'play_name': play_metadata['name'],
                'corpus': corpus,
                'type': 'cooccurrence_network',
                'data': cooccurrence_data,
                'title': play_metadata.get('title'),
                'author': play_metadata.get('author'),
                'year': play_metadata.get('year')
            }},
            upsert=True
        )
    
    # Store TEI XML
    if tei_data:
        tei_collection.update_one(
            {'play_name': play_metadata['name'], 'corpus': corpus},
            {'$set': {
                'play_name': play_metadata['name'],
                'corpus': corpus,
                'type': 'tei_xml',
                'xml': tei_data,
                'title': play_metadata.get('title'),
                'author': play_metadata.get('author'),
                'year': play_metadata.get('year')
            }},
            upsert=True
        )

def process_all_plays(corpus):
    """Process all plays in a corpus"""
    plays = get_all_plays_in_corpus(corpus)
    if not plays:
        print(f"No plays found for corpus {corpus}")
        return
    
    print(f"Found {len(plays)} plays in {corpus} corpus")
    
    for play in plays:
        play_name = play.get('name')
        if not play_name:
            continue
            
        print(f"\nProcessing: {play.get('title', play_name)}")
        
        # Download data
        csv_data = download_cooccurrence_csv(corpus, play_name)
        tei_data = download_tei_xml(corpus, play_name)
        
        # Store in MongoDB
        store_play_data(corpus, play, csv_data, tei_data)
        
        # Be polite with API requests
        time.sleep(1)
    
    print("\nAll plays processed successfully!")

if __name__ == "__main__":
    process_all_plays(CORPUS)