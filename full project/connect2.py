import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from lxml import etree
from pymongo import MongoClient

# Streamlit Configuration for the UI

st.set_page_config(page_title="Shakespeare Character Network", layout="wide")
st.title("Shakespeare Character Co-occurrence Network by Michelle and Joshua.")

# MongoDB Connection

MONGO_URI = "mongodb+srv://joshuaronaldino:Digital77@shakespear.hgzdqud.mongodb.net/?retryWrites=true&w=majority&appName=shakespear"
client = MongoClient(MONGO_URI)

db = client["shakespeare_db"]      
collection = db["plays"]
# Drop down box for plays and selecting them
play_titles = [doc["title"] for doc in collection.find({}, {"title": 1})]
selected_play = st.selectbox("Select a Play", play_titles)

# Load TEI XML from MongoDB

play_doc = collection.find_one({"title": selected_play})
tei_xml = play_doc["tei_xml"]   # This field contains the full TEI XML string

# Load and Apply XSLT

# Example XSLT as a string: converts TEI to simple HTML and applies more flavour lol
xslt_str = '''
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei">

  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <!-- Template to match the root -->
  <xsl:template match="/">
    <html>
      <head>
        <style>
          body { background-color: #fff9c4; font-family: Arial, sans-serif; color: #0d47a1; }
          h1, h2, h3 { color: #ff6f00; }
          .speaker { font-weight: bold; color: #d84315; }
          .line { margin-left: 20px; color: #1b5e20; }
          .scene { border: 2px solid #fbc02d; padding: 10px; margin-bottom: 20px; background-color: #fffde7;}
        </style>
      </head>
      <body>
        <h1><xsl:value-of select="tei:TEI/tei:text/tei:title"/></h1>
        <xsl:apply-templates select="tei:TEI/tei:text/tei:body/tei:div[@type='scene']"/>
      </body>
    </html>
  </xsl:template>

  <!-- Template for scene -->
  <xsl:template match="tei:div[@type='scene']">
    <div class="scene">
      <h2>Scene <xsl:number count="tei:div[@type='scene']"/></h2>
      <xsl:apply-templates select="tei:sp"/>
    </div>
  </xsl:template>

  <!-- Template for speeches -->
  <xsl:template match="tei:sp">
    <p>
      <span class="speaker">
        <xsl:value-of select="tei:speaker"/>
      </span>
      <xsl:apply-templates select="tei:p" />
    </p>
  </xsl:template>

  <!-- Template for paragraphs -->
  <xsl:template match="tei:p">
    <span class="line">
      <xsl:value-of select="."/>
    </span>
  </xsl:template>

</xsl:stylesheet>
'''

# Parse XML and XSLT
xml_tree = etree.fromstring(tei_xml.encode('utf-8'))
xslt_tree = etree.XML(xslt_str.encode('utf-8'))
transform = etree.XSLT(xslt_tree)

# Apply transformation
html_result = transform(xml_tree)
html_str = str(html_result)

# Show Transformed HTML in Streamlit

st.markdown("### Play Text (Transformed with XSLT)", unsafe_allow_html=True)
st.markdown(html_str, unsafe_allow_html=True)

# Extract Characters (Speakers) for Network

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
scenes = xml_tree.xpath("//tei:div[@type='scene']", namespaces=ns)
scene_options = [f"Scene {i+1}" for i in range(len(scenes))]
selected_scene = st.selectbox("Select a Scene", scene_options)

scene_index = scene_options.index(selected_scene)
scene = scenes[scene_index]

speakers = scene.xpath(".//tei:sp/@who", namespaces=ns)
speakers = [s.strip("#") for s in speakers if s]

unique_speakers = list(set(speakers))
pairs = []
for i in range(len(unique_speakers)):
    for j in range(i + 1, len(unique_speakers)):
        pairs.append((unique_speakers[i], unique_speakers[j]))

df = pd.DataFrame(pairs, columns=["Source", "Target"])
df["Weight"] = 1
df = df.groupby(["Source", "Target"], as_index=False).sum()

max_weight = int(df["Weight"].max())

if max_weight <= 1:
    st.write("All co-occurrences have weight 1.")
    min_weight = 1
else:
    min_weight = st.slider("Minimum Co-occurrence Weight", 1, max_weight, 1)

filtered_df = df[df["Weight"] >= min_weight]


# Build and Render Network

G = nx.Graph()
for _, row in filtered_df.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['Weight'])

net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="#0d47a1")
net.from_nx(G)

for node in net.nodes:
    node["title"] = node["id"]
    node["value"] = G.degree(node["id"])
    node["color"] = "#ff00e6"
    node["font"] = {"color": "#460da1", "size": 16}

net.save_graph("network.html")
HtmlFile = open("network.html", "r", encoding='utf-8')
components.html(HtmlFile.read(), height=750)
