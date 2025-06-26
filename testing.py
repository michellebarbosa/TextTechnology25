from pymongo import MongoClient
from pymongo.errors import OperationFailure
from urllib.parse import quote_plus

# Escape username/password (critical if special chars exist)
username = quote_plus("testingco")
password = quote_plus("Ilovescience08")  # <-- Replace with actual password

# Updated connection string
connection_string = (
    f"mongodb+srv://{username}:{password}@"
    "shakespear.hgzdqud.mongodb.net/"
    "?retryWrites=true&w=majority"
)

# Initialize variables to None (to avoid NameError)
client = None
db = None

try:
    client = MongoClient(connection_string)
    client.admin.command("ping")  # Test connection
    print("✅ Successfully connected to MongoDB Atlas!")
    
    db = client["dracor_db"]
    plays_collection = db["plays"]
    corpora_collection = db["corpora"]

    # --- TEST CONNECTION ---
    print("Collections in 'dracor_db':", db.list_collection_names())

except OperationFailure as e:
    print(f"❌ Connection failed: {e}")
    print("Check:")
    print("1. Username/password in Atlas → Database Access")
    print("2. IP whitelisting in Atlas → Network Access")
    print("3. User has readWrite permissions")
    exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)

# --- REST OF YOUR CODE ---
# Now you can safely use `db`, `plays_collection`, etc.
if db is not None:
    print("\nReady to use MongoDB collections!")
    print("Example: plays_collection.insert_one({...})")
else:
    print("Database connection failed. Check logs above.")