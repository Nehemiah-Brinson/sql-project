CREATE TABLE Movies (
    movie_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255),
    year INT,
    runtime INT,
    rating FLOAT
);

CREATE TABLE user_query_history (
    id VARCHAR(64) NOT NULL,
    query_value VARCHAR(255) NOT NULL,
    query_type VARCHAR(30) NOT NULL,
    "TimeStamp" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Actors (
    actor_id VARCHAR(20) PRIMARY KEY,
    actor_name VARCHAR(255)
);

CREATE TABLE Movie_Actors (
    movie_id VARCHAR(20),
    actor_id VARCHAR(20),
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES Actors(actor_id)
);

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50)
);

CREATE TABLE Movie_Genres (
    movie_id VARCHAR(20),
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);
