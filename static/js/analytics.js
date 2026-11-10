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

    }
    catch(error) {

        console.error(error);

    }
}


async function loadTopGenres() {

    try {

        const response = await fetch("/analytics/top-genres");

        const genres = await response.json();

        const labels = genres.map(g => g.genre);
        const values = genres.map(g => g.count);

        const ctx = document
            .getElementById("genreChart")
            .getContext("2d");

        new Chart(ctx, {

            type: "bar",

            data: {
                labels: labels,

                datasets: [{
                    label: "Movies",
                    data: values,
                    backgroundColor: "#f59e0b"
                }]
            },

            options: {
                responsive: true,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }

        });

    }
    catch(error) {

        console.error(error);

    }
}

loadOverview();
loadTopGenres();