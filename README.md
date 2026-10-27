# IMDb Database Project (Neon + Flask + Python)

This project loads the full IMDb dataset into a Neon PostgreSQL database and exposes a Flask API for searching movies, actors, directors, and genres.

---

## 📁 Project Structure

SQL-Project/
|
|--app.py
|--etl_full.py
|-schema.sql
|-requirements.txt
|-index.html
|-imdb_data/
    |-title.basics.csv
    |-title.ratings.csv
    |-title.principals.csv
    |-name.basics.csv

---

## 🚀 Features

- Full IMDb dataset (movies, actors, directors, genres)
- Neon PostgreSQL cloud database
- Flask API with multiple search endpoints
- Front-end HTML page for testing API calls
- Safe ETL loader with progress bars and error handling

---

## 🔧 Installation

### 1. Install dependencies

pip install -r requirements.txt

### 2. Create your Neon database
- Create a Neon project
- Copy your connection string
- Paste it into `etl_full.py` and `app.py`

### 3. Load the IMDb dataset

Place the four Kaggle CSV files into:
SQL-Project/imdb_data/
Then run:
python etl_full.py

This loads:
- Movies  
- Genres  
- Actors  
- Directors  
- All relationships  

---

## ▶️ Run the API

Start Flask:

python app.py

API will run at:

http://127.0.0.1:5000 (127.0.0.1 in Bing)

---

## 🔍 API Endpoints

### Movie Search
GET /movie/<title>

### Actor Search
GET /actor/<name>

### Director Search
GET /director/<name>

### Genre Search
GET /genre/<genre>

### Genre + Actor Search
GET /genreActor/<actor>/<genre>

### Actor + Genre Search
GET /actorGenre/<genre>/<actor>

### Genre + Director Search
GET /genreDirector/<genre>/<director>

### Actor + Director Search
GET /actorDirector/<actor>/<director>

### Actor + Genre + Director Search
GET /actorGenreDirector/<actor>/<genre>/<director>

### Recommendations
GET /recommendation

The recommendation endpoint reads from `user_query_history`. Search endpoints
automatically add the user's movie, actor, director, and genre queries to this
table. The API creates the table automatically if it is missing from the
connected PostgreSQL database. Cause I kept typing the name wrong

### API Home
GET /

---

## 🌐 Front-End

The Flask app serves a responsive movie discovery UI at the API root:

1. Start the app with `python app.py`.
2. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

The UI supports title, actor, director, and genre searches, combinations of
those filters, and personalized recommendations based on the current browser's
search history.

---

## 👥 Authors

- Austin Norris  
- Nehehmiah Brinson

---

## 📌 Notes

- ETL can be stopped and restarted safely.
- All inserts use `ON CONFLICT DO NOTHING` to avoid duplicates.
- ETL includes progress bars using `tqdm`.

---

## ✔ Status

Project is fully functional and ready for presentation.
