CREATE TABLE Movies (
    movie_id VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    year INT CHECK (year > 1800),
    runtime INT,
    rating FLOAT
);

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name TEXT UNIQUE NOT NULL
);

CREATE TABLE Movie_Generes (
    movie_id VARCHAR(20) REFERENCES Movies(movie_id),
    genre-id INT REFERENCES Genres(genre_id),
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE Actors(
    actor_id VARCHAR(20) PRIMARY KEY,
    actor_name TEXT NOT NULL
);

CREATE TABLE Movie_Actors (
    movie_id VARCHAR(20) REFERENCES Movies(movie_id),
    actor_id VARCHAR(20) REFERENCES Actors(actor_id),
    PRIMARY KEY (movie_id, actor_id)
);

CREATE TABLE Directors (
    director_id VARCHAR(20) PRIMARY KEY,
    director_name TEXT NOT NULL
);

CREATE TABLE Movie_Directors (
    movie_id VARCHAR(20) REFERENCES Movies(movie_id),
    director_id VARCHAR(20) REFERENCES Directors(director_id),
    PRIMARY KEY (movie_id, director_id)
);

CREATE TABLE User_Query_History(
    query_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    query_type TEXT CHECK (query_type IN ('movie','actor','genre')),
    query_value TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);