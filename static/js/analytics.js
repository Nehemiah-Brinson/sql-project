async function loadOverview() {

    try {

        const response = await fetch("/analytics/overview");

        const data = await response.json();

        document.getElementById("movies-card").textContent =
            data.movies.toLocaleString();

        document.getElementById("actors-card").textContent =
            data.actors.toLocaleString();

        document.getElementById("directors-card").textContent =
            data.directors.toLocaleString();

        document.getElementById("genres-card").textContent =
            data.genres.toLocaleString();

    } catch(error) {

        console.error(error);

        document.getElementById("movies-card").textContent = "Error";
        document.getElementById("actors-card").textContent = "Error";
        document.getElementById("directors-card").textContent = "Error";
        document.getElementById("genres-card").textContent = "Error";
    }
}

loadOverview();
