import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
from pymongo.errors import OperationFailure
import time

# =====================================
# 1. CONFIGURATION
# =====================================
DRACOR_API = "https://dracor.org/api/v1"
CORPUS_NAME = "shake"  # Shakespeare corpus
HEADERS = {"Accept": "application/json"}

# MongoDB configuration
MONGODB_URI = "mongodb+srv://testingco:Ilovescience08@shakespear.hgzdqud.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "shakespeare_db"
COLLECTION_NAME = "plays"

# =====================================
# 2. DRACOR API FUNCTIONS
# =====================================
def get_all_plays():
    #Fetch metadata for all plays in the Shakespeare corpus
    url = f"{DRACOR_API}/corpora/{CORPUS_NAME}/metadata"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch plays: {e}")
        return None

def get_play_tei(play_name):
    #Fetch TEI/XML for a specific play
    url = f"{DRACOR_API}/corpora/{CORPUS_NAME}/plays/{play_name}/tei"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch TEI for {play_name}: {e}")
        return None

# =====================================
# 3. MONGODB FUNCTIONS (FIXED)
# =====================================
def get_mongodb_collection():
    #stablish MongoDB connection and return collection
    try:
        client = MongoClient(MONGODB_URI)
        client.admin.command('ping')
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None

def store_play(collection, play_data):
    #tore or update a play in MongoDB
    try:
        result = collection.update_one(
            {"play_id": play_data["play_id"]},
            {"$set": play_data},
            upsert=True
        )
        return result.upserted_id or result.modified_count
    except Exception as e:
        print(f"Failed to store play: {e}")
        return False

# =====================================
# 4. MAIN PROCESSING (FIXED)
# =====================================
def transfer_plays():
    print("🚀 Starting Shakespeare play transfer...")
    
    # Step 1: Get MongoDB collection (FIXED)
    collection = get_mongodb_collection()
    if collection is None:  # Proper None check
        print("❌ Aborting: Could not connect to MongoDB")
        return
    
    # Step 2: Fetch all plays
    plays = get_all_plays()
    if plays is None:  # Proper None check
        print("❌ Aborting: Could not fetch plays from DraCor")
        return
    
    print(f"📚 Found {len(plays)} plays in the {CORPUS_NAME} corpus")
    
    # Step 3: Process each play
    success_count = 0
    for play in plays:
        play_name = play.get("name")
        print(f"\nProcessing: {play_name}...", end=" ")
        
        # Get TEI content
        tei_content = get_play_tei(play_name)
        if tei_content is None:  # Proper None check
            print("❌ Failed to get TEI content")
            continue
        
        # Prepare document
        play_data = {
            "play_id": play_name,
            "title": play.get("title", ""),
            "author": play.get("author", "William Shakespeare"),
            "year": play.get("year", ""),
            "genre": play.get("genre", ""),
            "tei_xml": tei_content,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "DraCor API"
        }
        
        # Store in MongoDB
        if store_play(collection, play_data):
            success_count += 1
            print("Done")
        else:
            print("Failed to store")
    
    # Final report
    print(f"\n🎉 Successfully transferred {success_count}/{len(plays)} plays")
    if success_count > 0:
        print(f"Total plays in database: {collection.count_documents({})}")

if __name__ == "__main__":
    transfer_plays()