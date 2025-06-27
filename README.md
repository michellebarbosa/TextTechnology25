# TextTechnology25
Repo for Text Technology using the Shakespear Drama Corpus

Setup

1. Clone the repository

git clone https://github.com/michellebarbosa/TextTechnology25.git
cd TextTechnology25

2. Install technologies
pip install -r requirements.txt
Run transferdataall.py for transfering all the plays to MongoDB
Run transferdata.py for transfering any one play of your choice to MongoDB


Creates MongoDB collection shakespeare_db.plays with:

Full TEI/XML texts

Play metadata (title, author, year)

Processing timestamps

Generates co-occurrence networks for character interactions

🛠 Troubleshooting
"Module not found": Reinstall dependencies with pip install -r requirements.txt

MongoDB connection issues:

Verify your IP is whitelisted in Atlas

Check .env file formatting (no quotes around values)
