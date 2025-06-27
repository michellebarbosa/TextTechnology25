import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Shakespeare Character Network", layout="wide")

st.title(" Shakespeare Character Co-occurrence Network")

# Load CSV
df = pd.read_csv("character_network.csv")

# Filters
min_weight = st.slider("Minimum Co-occurrence Weight", 1, int(df['Weight'].max()), 1)

# Filter data
filtered_df = df[df['Weight'] >= min_weight]

# Build Network
G = nx.Graph()
for _, row in filtered_df.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['Weight'])

# Create Pyvis Network
net = Network(height="700px", width="100%", bgcolor="#222222", font_color="white")
net.from_nx(G)

# Customize nodes
for node in net.nodes:
    node["title"] = node["id"]
    node["value"] = G.degree(node["id"])

# Save and render
net.save_graph("network.html")

# Display in Streamlit
HtmlFile = open("network.html", "r", encoding='utf-8')
components.html(HtmlFile.read(), height=750)
