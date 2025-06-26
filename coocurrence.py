import streamlit as st
from pymongo import MongoClient
from lxml import etree
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools
from textblob import TextBlob
import pandas as pd

# MongoDB Connection
@st.cache_resource
def get_db():
    client = MongoClient('mongodb+srv://testingco:Ilovescience08@shakespear.hgzdqud.mongodb.net/')
    return client['dracor_db'].plays

# Streamlit App
def main():
    st.title("🎭 Shakespeare Character Network Analyzer")
    
    # Sidebar controls
    st.sidebar.header("Controls")
    plays_collection = get_db()
    play_names = [play['play_name'] for play in plays_collection.find()]
    selected_play = st.sidebar.selectbox("Select Play", play_names)
    
    # Get TEI data from MongoDB
    play_data = plays_collection.find_one({"play_name": selected_play})
    tei_xml = play_data['tei_xml']
    
    # Process TEI
    with st.spinner(f"Analyzing {selected_play}..."):
        # Parse XML
        root = etree.fromstring(tei_xml.encode('utf-8'))
        ns = {'tei': root.nsmap[None]} if None in root.nsmap else {}
        
        # Extract data
        characters = set()
        character_lines = defaultdict(list)
        co_occurrence = defaultdict(int)
        
        scenes = root.xpath(".//tei:div[@type='scene']", namespaces=ns)
        for scene in scenes:
            speakers = set()
            for sp in scene.xpath(".//tei:sp", namespaces=ns):
                speaker = sp.xpath(".//tei:speaker/tei:w/text()", namespaces=ns)
                if speaker:
                    char_name = speaker[0].strip().upper()
                    speakers.add(char_name)
                    lines = sp.xpath(".//tei:p//text()", namespaces=ns)
                    character_lines[char_name].extend([line.strip() for line in lines if line.strip()])
            
            for pair in itertools.combinations(sorted(speakers), 2):
                co_occurrence[pair] += 1
        
        # Sentiment analysis
        character_sentiment = {
            char: TextBlob(' '.join(lines)).sentiment.polarity 
            for char, lines in character_lines.items()
        }
    
    # Create network graph
    G = nx.Graph()
    for (char1, char2), weight in co_occurrence.items():
        G.add_edge(char1, char2, weight=weight)
    
    # Visualization
    st.header(f"Character Network: {selected_play}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Network graph
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=500, 
               node_color=[character_sentiment.get(node, 0) for node in G.nodes()],
               cmap='coolwarm', edge_color='gray', alpha=0.8)
        plt.title("Character Co-occurrence Network")
        st.pyplot(plt)
    
    with col2:
        # Sentiment bar chart
        df_sentiment = pd.DataFrame.from_dict(character_sentiment, 
                                           orient='index', 
                                           columns=['Sentiment'])
        df_sentiment.sort_values('Sentiment', inplace=True)
        st.bar_chart(df_sentiment)
    
    # Data tables
    st.subheader("Network Data")
    
    # Edge list
    edges_df = pd.DataFrame(
        [(char1, char2, weight) for (char1, char2), weight in co_occurrence.items()],
        columns=['Character 1', 'Character 2', 'Shared Scenes']
    )
    st.dataframe(edges_df.sort_values('Shared Scenes', ascending=False))
    
    # Character metrics
    centrality = nx.degree_centrality(G)
    chars_df = pd.DataFrame({
        'Character': list(character_sentiment.keys()),
        'Sentiment': list(character_sentiment.values()),
        'Centrality': [centrality.get(char, 0) for char in character_sentiment.keys()],
        'Line Count': [len(character_lines[char]) for char in character_sentiment.keys()]
    })
    st.dataframe(chars_df.sort_values('Centrality', ascending=False))

if __name__ == "__main__":
    main()