from .spotify_auth import get_spotify_client
import datetime
import random

def get_listening_days():
    sp = get_spotify_client()
    results = sp.current_user_recently_played(limit=50)  
    if results and "items" in results:
        days_of_week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        listening_counts = {day: 0 for day in days_of_week.values()}

        for track in results["items"]:
            played_at = track["played_at"]
            date_obj = datetime.datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            day_of_week = date_obj.weekday()
            listening_counts[days_of_week[day_of_week]] += 1

        return listening_counts
    return {}

def get_recently_played():
    sp = get_spotify_client()
    results = sp.current_user_recently_played(limit=5)
    if results and "items" in results:
        tracks = [
            {
                "name": track["track"]["name"],
                "artist": track["track"]["artists"][0]["name"],
                "link": track["track"]["external_urls"]["spotify"]
            }
            for track in results["items"]
        ]
        return tracks
    return []

def get_top_artists():
    sp = get_spotify_client()
    results = sp.current_user_top_artists(limit=5)
    if results and "items" in results:
        artists = [
            {
                "name": artist["name"],
                "link": artist["external_urls"]["spotify"]
            }
            for artist in results["items"]
        ]
        return artists
    return []

# 🔹 Obtener los géneros principales
def get_top_genres():
    sp = get_spotify_client()
    results = sp.current_user_top_artists(limit=20)  
    genre_count = {}

    if results and "items" in results:
        for artist in results["items"]:
            for genre in artist["genres"]:
                genre_count[genre] = genre_count.get(genre, 0) + 1

        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return [{"name": genre, "count": count} for genre, count in sorted_genres[:5]]  # Top 5 géneros

    return []

# 🔹 Obtener trivia divertida sobre el historial musical
def get_music_trivia():
    sp = get_spotify_client()
    results = sp.current_user_top_tracks(limit=50)  

    if results and "items" in results:
        total_duration = sum(track["duration_ms"] for track in results["items"]) / 60000  # Minutos
        most_popular = max(results["items"], key=lambda x: x["popularity"])["name"]
        least_popular = min(results["items"], key=lambda x: x["popularity"])["name"]

        trivia = [
            f"Escuchaste un total de {int(total_duration)} minutos de tu Top 50",
            f"Tu canción más popular es '{most_popular}'",
            f"Tu joya oculta es '{least_popular}', pocos la conocen",
            f"Tienes un excelente gusto, escuchas canciones fuera del mainstream"
        ]

        return trivia

    return ["Necesitamos más datos para generar curiosidades. Sigue escuchando música."]

# 🔹 Obtener los podcasts más escuchados
def get_top_podcasts():
    sp = get_spotify_client()
    results = sp.current_user_top_artists(limit=10)  

    podcasts = [
        {"name": artist["name"], "link": artist["external_urls"]["spotify"]}
        for artist in results["items"] if "podcast" in artist["genres"]
    ]

    return podcasts[:5] if podcasts else [{"name": "No podcast data available!", "link": "#"}]

def search_track(track_name, limit=5):
    sp = get_spotify_client()
    results = sp.search(q=track_name, type="track", limit=limit)
    tracks = results["tracks"]["items"]

    if not tracks:
        print("No se ha encontrado la cancion.")
        return
    
    for idx, track in enumerate(tracks):
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        print(f"{idx+1}. {track['name']} - {artists}")
        print(f"   Spotify URL: {track['external_urls']['spotify']}")
        print(f"   Album: {track['album']['name']}")
        print("-" * 50)

# ==============================
# NUEVAS FUNCIONES PARA DASHBOARD
# ==============================

# 🔹 Mapa de calor de horas (7 días x 24 horas)
def get_listening_hours():
    sp = get_spotify_client()
    results = sp.current_user_recently_played(limit=50)
    heatmap_data = [[0 for _ in range(24)] for _ in range(7)]  # 7 días x 24 horas

    if results and "items" in results:
        for track in results["items"]:
            played_at = track["played_at"]
            date_obj = datetime.datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            weekday = date_obj.weekday()  # 0 = Monday
            hour = date_obj.hour
            heatmap_data[weekday][hour] += 1

    return heatmap_data

# 🔹 Minutos escuchados a un artista en el día
def get_artist_daily_minutes(artist_name):
    sp = get_spotify_client()
    today = datetime.datetime.utcnow().date()
    results = sp.current_user_recently_played(limit=50)

    total_minutes = 0
    if results and "items" in results:
        for track in results["items"]:
            played_at = datetime.datetime.strptime(track["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            if played_at == today:
                if any(artist_name.lower() in artist["name"].lower() for artist in track["track"]["artists"]):
                    total_minutes += track["track"]["duration_ms"] / 60000  

    return int(total_minutes)

# 🔹 Minutos totales en el mes actual
def get_monthly_listening():
    sp = get_spotify_client()
    now = datetime.datetime.utcnow()
    current_month = now.month
    results = sp.current_user_recently_played(limit=50)

    total_minutes = 0
    if results and "items" in results:
        for track in results["items"]:
            played_at = datetime.datetime.strptime(track["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if played_at.month == current_month:
                total_minutes += track["track"]["duration_ms"] / 60000  

    return int(total_minutes)


def get_song_playcount():
    sp = get_spotify_client()
    results = sp.current_user_recently_played(limit=50)

    playcount = {}
    if results and "items" in results:
        for track in results["items"]:
            song_name = track["track"]["name"]
            playcount[song_name] = playcount.get(song_name, 0) + 1

        if playcount:
            most_played = max(playcount.items(), key=lambda x: x[1])  # (canción, veces)
            return {"song": most_played[0], "count": most_played[1]}

    return {"song": None, "count": 0}
# 🔹 Artista más escuchado en el día y minutos totales
def get_top_artist_today():
    sp = get_spotify_client()
    today = datetime.datetime.utcnow().date()
    results = sp.current_user_recently_played(limit=50)

    artist_minutes = {}

    if results and "items" in results:
        for track in results["items"]:
            played_at = datetime.datetime.strptime(track["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            if played_at == today:
                for artist in track["track"]["artists"]:
                    name = artist["name"]
                    artist_minutes[name] = artist_minutes.get(name, 0) + (track["track"]["duration_ms"] / 60000)

        if artist_minutes:
            top_artist = max(artist_minutes.items(), key=lambda x: x[1])  # (artista, minutos)
            return {"artist": top_artist[0], "minutes": int(top_artist[1])}

    return {"artist": None, "minutes": 0}
