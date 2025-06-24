import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import defaultdict
from pymongo import MongoClient
from pydracor import DraCor

st.title("🎭 Shakespeare Character Network + Sentiment")

# Initialize DraCor client
dracor = DraCor()

# Get all corpora metadata (list of dicts)
corpora = dracor.corpora(include='metrics')

# Find Shakespeare corpus dict (name == 'shake')
shake_corpus = next(c for c in corpora if c['name'] == 'shake')

# Get list of play IDs in Shakespeare corpus
plays = shake_corpus['play_ids']

# Fetch one play - Macbeth
play = dracor.play(play_name='Macbeth', corpus_name='shake')

# Extract spoken text by character
char_text = play.spoken_text_by_character()

# Connect to MongoDB
client = MongoClient(st.secrets["mongo_uri"])
db = client["shakespeare_db"]
collection = db["plays"]

# Prepare document for MongoDB
doc = {
    "title": play.play_title,
    "corpus": "shake",
    "characters": [
        {"name": char, "text": text}
        for char, text in char_text.items()
    ]
}

# Insert document if not already inserted (optional check)
if collection.count_documents({"title": play.play_title}) == 0:
    collection.insert_one(doc)

# Retrieve the play document from DB
play_doc = collection.find_one({"title": "Macbeth"})
st.title(f"📖 {play_doc['title']}")

# Compute average sentiment polarity per character
avg_sent = {}
for ch in play_doc["characters"]:
    texts = ch["text"]
    # Defensive: check if texts is not empty
    if texts:
        scores = [TextBlob(t).sentiment.polarity for t in texts]
        avg_sent[ch["name"]] = sum(scores) / len(scores)
    else:
        avg_sent[ch["name"]] = 0.0

st.subheader("Sentiments")
st.json(avg_sent)

# Build a simple character co-occurrence network by sequential edges
G = nx.Graph()
chars = [ch["name"] for ch in play_doc["characters"]]
for i in range(len(chars) - 1):
    G.add_edge(chars[i], chars[i + 1])

st.subheader("Character Network")
fig, ax = plt.subplots(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color='skyblue', ax=ax)
st.pyplot(fig)
