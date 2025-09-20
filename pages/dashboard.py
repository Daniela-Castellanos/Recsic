from dash import html, dcc, callback, Input, Output 
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from src.spotify.spotify_data import (
    get_top_genres, 
    get_music_trivia, 
    get_top_podcasts, 
    get_listening_days,
    get_listening_hours,
    get_top_artist_today,
    get_monthly_listening,
    get_song_playcount
)

# Datos desde Spotify
top_genres = get_top_genres()
trivia_facts = get_music_trivia()
top_podcasts = get_top_podcasts()
listening_days = get_listening_days()
listening_hours = get_listening_hours()
top_artist_today = get_top_artist_today()
monthly_listening = get_monthly_listening()
song_playcount = get_song_playcount()

# Gráfico de hábitos por días
days, counts = (list(listening_days.keys()), list(listening_days.values())) if listening_days else ([], [])
listening_days_graph = {
    "data": [go.Bar(x=days, y=counts, marker=dict(color="#1DB954"))],
    "layout": go.Layout(title="Hábitos musicales", xaxis_title="Día", yaxis_title="Canciones escuchadas", height=400)
}

# Gráfico de géneros
genres_graph = px.pie(
    names=[genre["name"] for genre in top_genres],
    values=[genre["count"] for genre in top_genres],
    title="Top Géneros",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.Blues
)

# Heatmap de horas
if listening_hours:
    heatmap_fig = px.imshow(
        listening_hours,
        labels=dict(x="Hora del día", y="Día de la semana", color="Canciones"),
        x=[f"{h}:00" for h in range(24)],
        y=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"],
        color_continuous_scale="Greens",
        title="Mapa de calor de horas de escucha"
    )
else:
    heatmap_fig = go.Figure()

# Layout del Dashboard
dashboard_layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Spotify Dashboard", className="text-center text-white bg-dark p-4 mb-4 rounded"), width=12)]),

        dbc.Row([dbc.Col(dbc.Card([
            dbc.CardHeader("Dashboard Overview", className="bg-primary text-white"),
            dbc.CardBody([
                # Gráficos principales
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=genres_graph), width=6),
                    dbc.Col(dcc.Graph(figure=listening_days_graph), width=6)
                ]),
                html.Hr(),
                # Heatmap
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=heatmap_fig), width=12)
                ]),
                html.Hr(),
                # Estadísticas personalizadas
                dbc.Row([
                    dbc.Col(html.H3("Estadísticas Detalladas", className="text-center"), width=12),
                    dbc.Col(html.P(
                        f"Hoy escuchaste a {top_artist_today['artist']} {top_artist_today['minutes']} minutos" 
                        if top_artist_today["artist"] else "Hoy no escuchaste música",
                        className="text-center"
                    ), width=12),
                    dbc.Col(html.P(
                        f"Este mes llevas {monthly_listening} minutos de música",
                        className="text-center"
                    ), width=12),
                    dbc.Col(html.P(
                        f"La canción más escuchada fue '{song_playcount['song']}' con {song_playcount['count']} reproducciones"
                        if song_playcount["song"] else "No hay canción destacada todavía",
                        className="text-center"
                    ), width=12),
                ]),
                html.Hr(),
                # Trivia musical
                dbc.Row([
                    dbc.Col(html.H3("Trivia musical!", className="text-center"), width=12),
                    dbc.Col(html.Div(id="trivia-container", className="text-center text-muted mb-3"), width=12),
                    dbc.Col(dbc.Button("Random Trivia", id="trivia-button", color="primary", className="mt-2"), width=12, className="text-center")
                ]),
                html.Hr(),
                # Top podcasts
                dbc.Row([
                    dbc.Col(html.H3("Top Podcasts", className="text-center"), width=12),
                    dbc.Col(html.Ul([
                        html.Li(html.A(podcast["name"], href=podcast["link"], target="_blank", className="text-decoration-none text-primary")) for podcast in top_podcasts
                    ]), width=12)
                ])
            ])
        ], className="shadow mb-4"))]),

        dbc.Row([dbc.Col(dbc.Button("Inicio", href="/", color="secondary", className="mt-3"), width=12, className="text-center")])
    ], className="p-4")
])

# Callback para trivia
@callback(
    Output("trivia-container", "children"),
    Input("trivia-button", "n_clicks")
)
def show_random_trivia(n_clicks):
    if n_clicks:
        return html.P(f"{trivia_facts[n_clicks % len(trivia_facts)]}", style={"fontSize": "18px", "fontStyle": "italic"})
    return html.P("Selecciona el botón para un dato curioso!", style={"fontSize": "18px", "fontStyle": "italic"})
