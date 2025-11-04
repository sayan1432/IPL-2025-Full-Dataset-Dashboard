import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="WELCOME IPL 2025 DASHBOARD", layout="wide")
st.title("IPL 2025 Full Dataset Viewer")

# Load data
batting_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\orangecap.csv", encoding="ISO-8859-1")
bowling_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\purplecap.csv", encoding="ISO-8859-1", on_bad_lines='skip')
points_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\win.csv", encoding="ISO-8859-1", on_bad_lines='skip')
auction_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\ipl auction.csv", encoding="ISO-8859-1", on_bad_lines='skip')
teams_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\teams.csv", encoding="ISO-8859-1", on_bad_lines='skip')
schedule_df = pd.read_csv(r"C:\Users\Sayan Sil\OneDrive\Desktop\ipl25\data\schedule.csv", encoding="ISO-8859-1", sep=r"\s{2,}", engine='python', on_bad_lines='skip')

# Clean column names
schedule_df.columns = schedule_df.columns.str.strip()
bowling_df.columns = bowling_df.columns.str.strip()
points_df.columns = points_df.columns.str.strip()

# Sidebar controls
dataset = st.sidebar.selectbox("Select Dataset", ["Most Runs", "Most Wickets", "Points Table", "Players", "Teams", "Schedule"])
show_chart = st.sidebar.checkbox("Show Leaderboard Charts")

# Most Runs
if dataset == "Most Runs":
    st.subheader("Most Runs")
    st.dataframe(batting_df)

    if show_chart:
        st.subheader("Orange Cap Leaderboard")
        top_batters = batting_df.sort_values(by="Runs", ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(top_batters["Player"], top_batters["Runs"], color="orange")
        ax.set_xlabel("Runs")
        ax.set_ylabel("Player")
        ax.set_title("Top Run Scorers - IPL 2025")
        st.pyplot(fig)

# Most Wickets
elif dataset == "Most Wickets":
    st.subheader("Most Wickets")
    st.dataframe(bowling_df)

    if show_chart:
        st.subheader("Purple Cap Leaderboard")
        top_bowlers = bowling_df.sort_values(by="Wkts", ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(top_bowlers["Player"], top_bowlers["Wkts"], color="purple")
        ax.set_xlabel("Wickets")
        ax.set_ylabel("Player")
        ax.set_title("Top Wicket Takers - IPL 2025")
        st.pyplot(fig)

# Points Table
elif dataset == "Points Table":
    st.subheader("Points Table")
    st.dataframe(points_df)

    if show_chart:
        st.subheader("Team Win Distribution")

        # Detect team column
        M_col = 'M' if 'M' in points_df.columns else points_df.columns[0]

        # Prepare data
        labels = points_df[M_col].astype(str).str.strip()
        wins = points_df["W"]

        # Plot pie chart
        fig, ax = plt.subplots()
        ax.pie(wins, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)


# Players
elif dataset == "Players":
    st.subheader("Auctions")
    st.dataframe(auction_df)

# Teams
elif dataset == "Teams":
    st.subheader("Team Info")
    st.dataframe(teams_df)

# Schedule
elif dataset == "Schedule":
    st.subheader("Match Schedule")

    # Detect team columns
    team_cols = [col for col in schedule_df.columns if "Home" in col or "Away" in col]
    if len(team_cols) < 2:
        st.error("Could not detect Home and Away team columns.")
        st.stop()

    home_col, away_col = team_cols[0], team_cols[1]

    # Clean team names
    schedule_df[home_col] = schedule_df[home_col].astype(str).str.strip().str.lower()
    schedule_df[away_col] = schedule_df[away_col].astype(str).str.strip().str.lower()

    # Unique teams
    all_teams_raw = pd.unique(schedule_df[[home_col, away_col]].values.ravel('K'))
    all_teams_clean = [team.title().strip() for team in all_teams_raw if isinstance(team, str) and team.strip() != ""]

    # Select teams
    st.subheader("Select Teams to Compare")
    selected_home = st.selectbox("Select Home Team", sorted(all_teams_clean))
    selected_away = st.selectbox("Select Away Team", sorted(all_teams_clean))

    selected_home_clean = selected_home.strip().lower()
    selected_away_clean = selected_away.strip().lower()

    # Filter matches
    match_df = schedule_df[
        ((schedule_df[home_col] == selected_home_clean) & (schedule_df[away_col] == selected_away_clean)) |
        ((schedule_df[home_col] == selected_away_clean) & (schedule_df[away_col] == selected_home_clean))
    ].copy()

    # Convert date
    date_col = 'Date' if 'Date' in schedule_df.columns else schedule_df.columns[-1]
    match_df[date_col] = pd.to_datetime(match_df[date_col], errors='coerce')
    match_df = match_df.sort_values(date_col)

    # Detect venue column
    venue_col_candidates = [col for col in schedule_df.columns if any(key in col.lower() for key in ["venue", "ground", "location"])]
    venue_col = venue_col_candidates[0] if venue_col_candidates else None

    # Display match info
    st.subheader(f"Matches between {selected_home} and {selected_away}")
    if match_df.empty:
        st.warning("No matches found between these teams.")
    else:
        st.write("Match Details:")
        for _, row in match_df.iterrows():
            dt = row[date_col]
            venue = row[venue_col] if venue_col and pd.notnull(row[venue_col]) else "Unknown Venue"
            if pd.notnull(dt):
                st.markdown(f"- **Date: {dt.strftime('%d %b %Y')}** | Venue: {venue}")
            else:
                st.markdown(f"- **Unknown Date** | Venue: {venue}")
