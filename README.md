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

### API Home
GET /

---

## 🌐 Front-End (index.html)

Open `index.html` in a browser to test the API with a simple UI.

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
