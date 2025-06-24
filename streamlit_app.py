import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import defaultdict
from pymongo import MongoClient

st.title("🎭 Shakespeare Character Network + Sentiment")


from pydracor import DraCor

# Initialize API client
dracor = DraCor()

# List available Shakespeare plays
corpora = dracor.corpora_names()
# corpora includes 'shake' for Shakespeare

plays = dracor.corpora(include='metrics')['shake']['play_ids']

# Fetch one play
play = dracor.play(play_name='Macbeth', corpus_name='shake')

# Extract character spoken text
char_text = play.spoken_text_by_character()

from pymongo import MongoClient

client = MongoClient(st.secrets["mongo_uri"])
db = client["shakespeare_db"]
collection = db["plays"]

doc = {
    "title": play.play_title,
    "corpus": "shake",
    "characters": [
        {"name": char, "text": text}
        for char, text in char_text.items()
    ]
}

collection.insert_one(doc)

import streamlit as st
from pymongo import MongoClient
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import defaultdict

# Connect to MongoDB
client = MongoClient(st.secrets["mongo_uri"])
collection = client["shakespeare_db"]["plays"]

# Select a play
play = collection.find_one({"title": "Macbeth"})
st.title(f"📖 {play['title']}")

# Compute sentiment per character
avg_sent = {}
for ch in play["characters"]:
    texts = ch["text"]
    scores = [TextBlob(t).sentiment.polarity for t in texts]
    avg_sent[ch["name"]] = sum(scores)/len(scores)

st.subheader("Sentiments")
st.json(avg_sent)

# Build a simple character co-occurrence network
G = nx.Graph()
chars = [ch["name"] for ch in play["characters"]]
for i in range(len(chars)-1):
    G.add_edge(chars[i], chars[i+1])

st.subheader("Character Network")
fig, ax = plt.subplots()
nx.draw(G, with_labels=True, node_color='skyblue', ax=ax)
st.pyplot(fig)




