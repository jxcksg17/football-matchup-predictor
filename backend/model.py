import numpy as np
import pandas as pd
from scipy.stats import poisson

class ApexScoutEngine:
    def __init__(self, data_path: str, half_life_days: float = 730.0):
        self.half_life_days = half_life_days
        self.df = self._load_data(data_path)
        self.teams = sorted(list(set(self.df['home_team']).union(set(self.df['away_team']))))
        self.elo_ratings = {}
        self.team_stats = {}
        self.home_advantage = 0.25
        self._compute_elo_and_stats()

    def _load_data(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.dropna(subset=['home_score', 'away_score'])
        # Sort chronologically for dynamic Elo tracking
        df = df.sort_values('date').reset_index(drop=True)
        return df

    def _compute_elo_and_stats(self):
        # Base Elo initialization
        for t in self.teams:
            self.elo_ratings[t] = 1500.0
            self.team_stats[t] = {'scored': 0, 'conceded': 0, 'matches': 0}

        max_date = self.df['date'].max()

        for _, row in self.df.iterrows():
            h, a = row['home_team'], row['away_team']
            h_score, a_score = int(row['home_score']), int(row['away_score'])
            
            # Elo update
            r_h = self.elo_ratings[h] + 60 # Home advantage boost
            r_a = self.elo_ratings[a]
            
            e_h = 1.0 / (1.0 + 10 ** ((r_a - r_h) / 400.0))
            e_a = 1.0 - e_h
            
            if h_score > a_score:
                s_h, s_a = 1.0, 0.0
            elif h_score == a_score:
                s_h, s_a = 0.5, 0.5
            else:
                s_h, s_a = 0.0, 1.0

            # Weight by tournament type
            k = 30.0 if 'World Cup' in str(row['tournament']) else (20.0 if 'Friendly' not in str(row['tournament']) else 10.0)
            
            self.elo_ratings[h] += k * (s_h - e_h)
            self.elo_ratings[a] += k * (s_a - e_a)

    def predict(self, home_team: str, away_team: str, neutral: bool = False, max_goals: int = 7):
        if home_team not in self.elo_ratings or away_team not in self.elo_ratings:
            raise ValueError("Team not found in database.")

        elo_h = self.elo_ratings[home_team] + (0.0 if neutral else 65.0)
        elo_a = self.elo_ratings[away_team]

        elo_diff = (elo_h - elo_a) / 400.0
        
        # Base international average goal expectation (~1.35 goals per side)
        base_goal_rate = 1.35
        
        # Elo-adjusted expected goals (lambda)
        lambda_home = max(0.08, base_goal_rate * (10 ** (0.28 * elo_diff)))
        lambda_away = max(0.08, base_goal_rate * (10 ** (-0.28 * elo_diff)))

        # Score probability matrix (Dixon-Coles low-score correction)
        home_probs = [poisson.pmf(i, lambda_home) for i in range(max_goals)]
        away_probs = [poisson.pmf(j, lambda_away) for j in range(max_goals)]
        matrix = np.outer(home_probs, away_probs)

        # Dixon-Coles adjustment for rho (draw correlation)
        rho = -0.04
        if matrix.shape[0] > 1 and matrix.shape[1] > 1:
            matrix[0, 0] = max(0.0, matrix[0, 0] * (1.0 - lambda_home * lambda_away * rho))
            matrix[0, 1] = max(0.0, matrix[0, 1] * (1.0 + lambda_home * rho))
            matrix[1, 0] = max(0.0, matrix[1, 0] * (1.0 + lambda_away * rho))
            matrix[1, 1] = max(0.0, matrix[1, 1] * (1.0 - rho))
            matrix = matrix / np.sum(matrix) # Normalize

        p_home = float(np.sum(np.tril(matrix, -1)))
        p_draw = float(np.sum(np.diag(matrix)))
        p_away = float(np.sum(np.triu(matrix, 1)))

        # Find top 3 most likely scorelines
        top_scores = []
        for r in range(max_goals):
            for c in range(max_goals):
                top_scores.append({"score": f"{r} - {c}", "prob": round(float(matrix[r, c]) * 100, 1)})
        top_scores = sorted(top_scores, key=lambda x: x['prob'], reverse=True)[:4]

        return {
            "home_team": home_team,
            "away_team": away_team,
            "elo_home": round(self.elo_ratings[home_team]),
            "elo_away": round(self.elo_ratings[away_team]),
            "lambda_home": round(lambda_home, 2),
            "lambda_away": round(lambda_away, 2),
            "prob_home_win": round(p_home * 100, 1),
            "prob_draw": round(p_draw * 100, 1),
            "prob_away_win": round(p_away * 100, 1),
            "top_scores": top_scores,
            "matrix": [[round(float(val) * 100, 2) for val in row] for row in matrix]
        }
