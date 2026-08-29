const API_URL = "http://127.0.0.1:8000/api";
let currentScope = "international";

function setScope(scope) {
  currentScope = scope;
  document.getElementById("scope-club").classList.toggle("active", scope === "club");
  document.getElementById("scope-intl").classList.toggle("active", scope === "international");
  document.getElementById("results").style.display = "none";
  loadTeams();
}

async function loadTeams() {
  const homeSelect = document.getElementById("home-select");
  const awaySelect = document.getElementById("away-select");
  
  homeSelect.innerHTML = "<option>Loading teams...</option>";
  awaySelect.innerHTML = "<option>Loading teams...</option>";

  try {
    const res = await fetch(`${API_URL}/teams?scope=${currentScope}`);
    if (!res.ok) throw new Error(`Backend error: ${res.statusText}`);
    
    const data = await res.json();
    homeSelect.innerHTML = "";
    awaySelect.innerHTML = "";

    if (!data.teams || data.teams.length === 0) {
      homeSelect.innerHTML = "<option>No teams found</option>";
      awaySelect.innerHTML = "<option>No teams found</option>";
      return;
    }

    data.teams.forEach(team => {
      homeSelect.add(new Option(team, team));
      awaySelect.add(new Option(team, team));
    });

    // Set intelligent defaults
    if (currentScope === "club") {
      homeSelect.value = data.teams.includes("Arsenal") ? "Arsenal" : data.teams[0];
      awaySelect.value = data.teams.includes("Chelsea") ? "Chelsea" : (data.teams[1] || data.teams[0]);
    } else {
      homeSelect.value = data.teams.includes("Brazil") ? "Brazil" : data.teams[0];
      awaySelect.value = data.teams.includes("Argentina") ? "Argentina" : (data.teams[1] || data.teams[0]);
    }
  } catch (err) {
    console.error("Failed to load teams:", err);
    homeSelect.innerHTML = "<option>Backend not reachable</option>";
    awaySelect.innerHTML = "<option>Backend not reachable</option>";
    alert("Could not connect to FastAPI backend at http://127.0.0.1:8000. Make sure uvicorn is running!");
  }
}

async function executePrediction() {
  const home = document.getElementById("home-select").value;
  const away = document.getElementById("away-select").value;

  if (home === away) {
    alert("Please select two distinct teams.");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/predict?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}&scope=${currentScope}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Prediction failed");
    }
    const data = await res.json();

    document.getElementById("results").style.display = "block";
    document.getElementById("home-title").innerText = data.home_team;
    document.getElementById("away-title").innerText = data.away_team;
    document.getElementById("home-elo").innerText = `Elo: ${data.elo_home}`;
    document.getElementById("away-elo").innerText = `Elo: ${data.elo_away}`;
    document.getElementById("home-xg").innerText = `xG: ${data.lambda_home}`;
    document.getElementById("away-xg").innerText = `xG: ${data.lambda_away}`;

    document.getElementById("home-prob-text").innerText = `${data.prob_home_win}%`;
    document.getElementById("draw-prob-text").innerText = `Draw ${data.prob_draw}%`;
    document.getElementById("away-prob-text").innerText = `${data.prob_away_win}%`;

    document.getElementById("bar-home").style.width = `${data.prob_home_win}%`;
    document.getElementById("bar-draw").style.width = `${data.prob_draw}%`;
    document.getElementById("bar-away").style.width = `${data.prob_away_win}%`;

    const scoresContainer = document.getElementById("top-scores-list");
    scoresContainer.innerHTML = "";
    data.top_scores.forEach(item => {
      const row = document.createElement("div");
      row.className = "score-item";
      row.innerHTML = `<span>${item.score}</span><span class="prob-tag">${item.prob}%</span>`;
      scoresContainer.appendChild(row);
    });

    renderMatrix(data.matrix);
  } catch (err) {
    alert("Prediction error: " + err.message);
  }
}

function renderMatrix(matrix) {
  const container = document.getElementById("matrix-grid");
  container.innerHTML = "";
  const size = matrix.length;

  container.appendChild(createCell("H \\ A", "m-head"));
  for (let j = 0; j < size; j++) container.appendChild(createCell(`A${j}`, "m-head"));

  for (let i = 0; i < size; i++) {
    container.appendChild(createCell(`H${i}`, "m-head"));
    for (let j = 0; j < size; j++) {
      const val = matrix[i][j];
      const cls = val > 6.0 ? "m-high" : "";
      container.appendChild(createCell(`${val}%`, cls));
    }
  }
}

function createCell(text, extraClass = "") {
  const div = document.createElement("div");
  div.className = `m-cell ${extraClass}`;
  div.innerText = text;
  return div;
}

window.onload = loadTeams;
