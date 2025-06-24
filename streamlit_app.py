import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import defaultdict

st.title("🎭 Shakespeare Character Network + Sentiment")

# Dummy data (pretend lines from Shakespeare)
lines = [
    {"speaker": "HAMLET", "text": "To be, or not to be, that is the question."},
    {"speaker": "OPHELIA", "text": "O, what a noble mind is here o'erthrown!"},
    {"speaker": "HAMLET", "text": "Get thee to a nunnery."},
    {"speaker": "POLONIUS", "text": "Though this be madness, yet there is method in't."}
]

# Calculate sentiment per speaker
character_sentiments = defaultdict(list)
for line in lines:
    sentiment = TextBlob(line["text"]).sentiment.polarity
    character_sentiments[line["speaker"]].append(sentiment)

avg_sentiments = {
    char: round(sum(scores) / len(scores), 3) 
    for char, scores in character_sentiments.items()
}

st.subheader("💬 Average Sentiment per Character")
for char, score in avg_sentiments.items():
    st.write(f"**{char}:** {score}")

# Build simple character network (edges between consecutive speakers)
G = nx.Graph()
speakers = [line["speaker"] for line in lines]
for i in range(len(speakers)-1):
    if speakers[i] != speakers[i+1]:
        G.add_edge(speakers[i], speakers[i+1])

st.subheader("🕸️ Character Interaction Network")

fig, ax = plt.subplots()
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', ax=ax)
st.pyplot(fig)

