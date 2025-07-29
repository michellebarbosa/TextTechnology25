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



### Database Schema

The project uses a MongoDB database named `shakespeare_db` with a collection called `plays`. Each document in the collection has the following structure:

- **`title`**: (String) The title of the play.
- **`corpus`**: (String) The name of the DraCor corpus (e.g., 'shake').
- **`characters`**: (Array of Objects) A list of characters in the play.
  - **`name`**: (String) The name of the character.
  - **`text`**: (Array of Strings) A list containing all lines of dialogue for that character.
 
### Configuration

This application requires a `secrets.toml` file to store the MongoDB connection URI.

1.  Create a directory named `.streamlit` in the root of the project folder.
2.  Inside the `.streamlit` directory, create a file named `secrets.toml`.
3.  Add the following content to the `secrets.toml` file, replacing the placeholder with your own MongoDB connection string:

    ```toml
    # .streamlit/secrets.toml
    mongo_uri = "mongodb+srv://<user>:<password>@cluster.mongodb.net/your_db_name"
    ```


