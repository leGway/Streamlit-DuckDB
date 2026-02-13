import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go  # Pour des graphiques plus avancés (gauge, heatmap...)
from datetime import datetime       # Pour afficher la date de dernière mise à jour

# --- CONFIGURATION INITIALE ---
st.set_page_config(
    page_title="Data Analytics Hub",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HORODATAGE DE SESSION ---
# Stocke l'heure de début de session pour l'afficher plus tard
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now().strftime("%d/%m/%Y %H:%M")

# --- GESTION DU THÈME (DARK / LIGHT) ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    st.info("Chargez vos fichiers CSV ci-dessous.")
    # Le switch retourne True ou False
    dark_mode = st.toggle("🌙 Mode Sombre", value=False) 

# Définition des variables de couleur selon le mode choisi
if dark_mode:
    # Mode Sombre (Cyberpunk / Dev)
    bg_color = "#0E1117"
    card_bg = "#262730"
    text_color = "#FAFAFA"
    subtext_color = "#A3A8B8"
    border_color = "#3D3D3D"
    viz_template = "plotly_dark"  # Thème sombre pour Plotly
else:
    # Mode Clair (Corporate / Clean)
    bg_color = "#FFFFFF"
    card_bg = "#FFFFFF"
    text_color = "#1F2937"
    subtext_color = "#888888"
    border_color = "#E6E6E6"
    viz_template = "plotly_white" # Thème clair pour Plotly

# --- INJECTION CSS DYNAMIQUE ---
st.markdown(f"""
<style>
    /* Force le fond global */
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* Style des Cartes KPI */
    .kpi-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #FF4B4B;
    }}

    .kpi-title {{
        color: {subtext_color};
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}
    
    .kpi-value {{
        color: {text_color};
        font-size: 1.8rem;
        font-weight: 700;
    }}
    
    /* Adaptation globale des textes Streamlit */
    h1, h2, h3, p, li, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 1px solid {border_color};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
    }}
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS BACKEND ---

@st.cache_data
def load_data(file):
    """Charge le CSV et nettoie les noms de colonnes."""
    df = pd.read_csv(file)
    df.columns = [
        c.strip().replace(" ", "_").replace("-", "_").replace("?", "")
        .replace("(", "").replace(")", "").lower() 
        for c in df.columns
    ]
    return df

def download_button(df, filename, label="📥 Télécharger en CSV"):
    """Propose un bouton de téléchargement pour n'importe quel DataFrame."""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=label, data=csv, file_name=filename, mime='text/csv')

def display_kpi(col, title, value, subtext=None, color="green"):
    """Affiche une carte KPI HTML stylisée."""
    delta_html = f"<div style='color:{color}; font-size: 0.8rem; font-weight: 500; margin-top: 5px;'>{subtext}</div>" if subtext else ""
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def display_gauge(value, title, max_val=100, color="#FF4B4B"):
    """Affiche un indicateur de type jauge (gauge chart) avec Plotly."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': text_color}},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': subtext_color},
            'bar': {'color': color},
            'bgcolor': card_bg,
            'bordercolor': border_color,
        },
        number={'font': {'color': text_color}}
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- INITIALISATION DUCKDB ---
if "con" not in st.session_state:
    st.session_state.con = duckdb.connect(database=":memory:")
con = st.session_state.con

# --- HEADER & SIDEBAR ---
st.title(" Data Analytics Hub")
st.markdown("**Plateforme unifiée d'intelligence économique et sociale**")
st.markdown("---")

with st.sidebar:
    st.markdown("### 📂 Ingestion")
    file_amazon = st.file_uploader("Amazon Prime (CSV)", type="csv")
    if file_amazon:
        df_amazon = load_data(file_amazon)
        con.register("amazon", df_amazon)
        st.success("Amazon Ready ✅")

    file_mental = st.file_uploader("Mental Health (CSV)", type="csv")
    if file_mental:
        df_mental = load_data(file_mental)
        con.register("mental", df_mental)
        st.success("Mental Health Ready ✅")
        
    st.markdown("---")
    st.caption("v2.1.0 - Powered by DuckDB & Plotly")

    # --- INFO SESSION ---
    st.markdown("---")
    st.markdown(f"🕐 Session démarrée : `{st.session_state.session_start}`")
    
    # Bouton pour réinitialiser toutes les données chargées
    if st.button("🗑️ Réinitialiser les données"):
        st.session_state.con = duckdb.connect(database=":memory:")
        st.cache_data.clear()
        st.rerun()

# --- TABS PRINCIPAUX ---
tab_amazon, tab_mental = st.tabs(["🎬 Amazon Prime Intelligence", "🧠 Student Well-being Analysis"])

# =========================================================
# VUE 1 : AMAZON
# =========================================================
with tab_amazon:
    if "amazon" in [t[0] for t in con.execute("SHOW TABLES").fetchall()]:
        
        # Filtres
        years = con.execute("SELECT DISTINCT release_year FROM amazon ORDER BY release_year DESC").fetchdf()
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            selected_year = st.selectbox("Année d'analyse", years['release_year'], index=2)
            
        # Requêtes KPI
        total_titles = con.execute(f"SELECT count(*) FROM amazon WHERE release_year = {selected_year}").fetchone()[0]
        movies_count = con.execute(f"SELECT count(*) FROM amazon WHERE release_year = {selected_year} AND type='Movie'").fetchone()[0]
        tv_count = con.execute(f"SELECT count(*) FROM amazon WHERE release_year = {selected_year} AND type='TV Show'").fetchone()[0]
        top_rating = con.execute(f"SELECT rating FROM amazon WHERE release_year = {selected_year} GROUP BY rating ORDER BY count(*) DESC LIMIT 1").fetchone()
        
        # Affichage Cartes
        kpi_cols = st.columns(4)
        display_kpi(kpi_cols[0], "Contenu Total", total_titles, f"En {selected_year}")
        display_kpi(kpi_cols[1], "Films", movies_count, f"{round(movies_count/total_titles*100) if total_titles else 0}% du catalogue", "#3498db")
        display_kpi(kpi_cols[2], "Séries TV", tv_count, f"{round(tv_count/total_titles*100) if total_titles else 0}% du catalogue", "#e67e22")
        display_kpi(kpi_cols[3], "Rating Dominant", top_rating[0] if top_rating else "N/A", "Cible principale")

        st.markdown("###  Deep Dive Analytics")
        
        # Graphiques
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("**Top 10 Genres**")
            df_genres = con.execute(f"""
                SELECT listed_in as Genre, COUNT(*) as Count 
                FROM amazon WHERE release_year = {selected_year} 
                GROUP BY Genre ORDER BY Count DESC LIMIT 10
            """).fetchdf()
            
            # Note l'utilisation de template=viz_template ici !
            fig_bar = px.bar(df_genres, x="Count", y="Genre", orientation='h', 
                             text="Count", color="Count", color_continuous_scale="Blues",
                             template=viz_template)
            fig_bar.update_layout(xaxis_title="", yaxis_title="", showlegend=False, height=350)
            st.plotly_chart(fig_bar, use_container_width=True)

        with viz_col2:
            st.markdown("**Répartition Rating / Type**")
            df_sun = con.execute(f"""
                SELECT type, rating, count(*) as total 
                FROM amazon WHERE release_year = {selected_year} AND rating IS NOT NULL
                GROUP BY type, rating
            """).fetchdf()
            
            fig_sun = px.sunburst(df_sun, path=['type', 'rating'], values='total', color='type',
                                  template=viz_template)
            fig_sun.update_layout(height=350)
            st.plotly_chart(fig_sun, use_container_width=True)

        # Tendance Historique
        st.markdown("###  Tendance Historique (10 ans)")
        start_year = selected_year - 10
        df_trend = con.execute(f"""
            SELECT release_year, type, count(*) as total 
            FROM amazon 
            WHERE release_year BETWEEN {start_year} AND {selected_year}
            GROUP BY release_year, type
            ORDER BY release_year
        """).fetchdf()
        
        fig_line = px.area(df_trend, x="release_year", y="total", color="type", 
                           title=f"Volume de production ({start_year}-{selected_year})",
                           template=viz_template)
        st.plotly_chart(fig_line, use_container_width=True)

        # --- EXPORT & STATISTIQUES AVANCÉES ---
        st.markdown("### 📊 Statistiques Avancées")
        
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            # Top 5 des réalisateurs les plus prolifiques
            st.markdown("**Top 5 Réalisateurs**")
            df_directors = con.execute(f"""
                SELECT director as Réalisateur, COUNT(*) as Nb_Titres
                FROM amazon
                WHERE release_year = {selected_year} AND director IS NOT NULL AND director != ''
                GROUP BY director ORDER BY Nb_Titres DESC LIMIT 5
            """).fetchdf()
            st.dataframe(df_directors, use_container_width=True, hide_index=True)
        
        with adv_col2:
            # Top 5 des pays producteurs
            st.markdown("**Top 5 Pays Producteurs**")
            df_countries = con.execute(f"""
                SELECT country as Pays, COUNT(*) as Nb_Titres
                FROM amazon
                WHERE release_year = {selected_year} AND country IS NOT NULL AND country != ''
                GROUP BY country ORDER BY Nb_Titres DESC LIMIT 5
            """).fetchdf()
            st.dataframe(df_countries, use_container_width=True, hide_index=True)
        
        # Bouton de téléchargement des données filtrées
        df_export = con.execute(f"SELECT * FROM amazon WHERE release_year = {selected_year}").fetchdf()
        download_button(df_export, f"amazon_{selected_year}.csv", f"📥 Exporter données {selected_year}")

    else:
        st.info("Veuillez charger le fichier Amazon pour activer la vue Intelligence.")

# =========================================================
# VUE 2 : SANTÉ MENTALE
# =========================================================
with tab_mental:
    if "mental" in [t[0] for t in con.execute("SHOW TABLES").fetchall()]:
        st.header("Analyse Croisée : Facteurs de Stress")

        # KPIS SANTÉ
        stats = con.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN lower(do_you_have_depression) = 'yes' THEN 1 ELSE 0 END) as dep,
                SUM(CASE WHEN lower(do_you_have_anxiety) = 'yes' THEN 1 ELSE 0 END) as anx,
                SUM(CASE WHEN lower(do_you_have_panic_attack) = 'yes' THEN 1 ELSE 0 END) as panic
            FROM mental
        """).fetchone()
        
        mk_cols = st.columns(4)
        display_kpi(mk_cols[0], "Panel Étudiant", stats[0])
        display_kpi(mk_cols[1], "Dépression", f"{round(stats[1]/stats[0]*100) if stats[0] else 0}%", "Taux déclaré", "#e74c3c")
        display_kpi(mk_cols[2], "Anxiété", f"{round(stats[2]/stats[0]*100) if stats[0] else 0}%", "Taux déclaré", "#e67e22")
        display_kpi(mk_cols[3], "Attaques Panique", f"{round(stats[3]/stats[0]*100) if stats[0] else 0}%", "Taux déclaré", "#9b59b6")

        st.markdown("---")
        
        col_viz_m1, col_viz_m2 = st.columns(2)
        
        with col_viz_m1:
            st.markdown("####  Stress par Année d'Étude")
            df_year_anx = con.execute("""
                SELECT your_current_year_of_study as Year, do_you_have_anxiety as Anxiety, count(*) as Count
                FROM mental
                GROUP BY Year, Anxiety
            """).fetchdf()
            
            fig_stack = px.bar(df_year_anx, x="Year", y="Count", color="Anxiety", 
                               category_orders={"Year": ["year 1", "year 2", "year 3", "year 4"]},
                               color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"},
                               barmode="group",
                               template=viz_template)
            st.plotly_chart(fig_stack, use_container_width=True)

        with col_viz_m2:
            st.markdown("####  Impact du Genre")
            df_gender_dep = con.execute("""
                SELECT choose_your_gender as Gender, do_you_have_depression as Depression, count(*) as Count
                FROM mental
                GROUP BY Gender, Depression
            """).fetchdf()
            
            fig_pie = px.sunburst(df_gender_dep, path=['Gender', 'Depression'], values='Count',
                                  color='Depression', 
                                  color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"},
                                  template=viz_template)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- JAUGES VISUELLES ---
        st.markdown("#### 📈 Indicateurs Visuels")
        gauge_cols = st.columns(3)
        with gauge_cols[0]:
            display_gauge(round(stats[1]/stats[0]*100) if stats[0] else 0, "Dépression (%)", color="#e74c3c")
        with gauge_cols[1]:
            display_gauge(round(stats[2]/stats[0]*100) if stats[0] else 0, "Anxiété (%)", color="#e67e22")
        with gauge_cols[2]:
            display_gauge(round(stats[3]/stats[0]*100) if stats[0] else 0, "Panique (%)", color="#9b59b6")

        # --- HEATMAP : CGPA vs TROUBLES ---
        st.markdown("#### 🔥 Heatmap : CGPA vs Dépression")
        df_heatmap = con.execute("""
            SELECT what_is_your_cgpa as CGPA, do_you_have_depression as Depression, COUNT(*) as Count
            FROM mental
            WHERE what_is_your_cgpa IS NOT NULL
            GROUP BY CGPA, Depression
        """).fetchdf()
        fig_heat = px.density_heatmap(df_heatmap, x="CGPA", y="Depression", z="Count",
                                       color_continuous_scale="RdYlGn_r",
                                       template=viz_template)
        fig_heat.update_layout(height=300)
        st.plotly_chart(fig_heat, use_container_width=True)

        # EXPLORATEUR
        st.markdown("#### 🔬 Explorateur de Données")
        with st.expander("Ouvrir la table de données brute"):
            courses = con.execute("SELECT DISTINCT what_is_your_course FROM mental").fetchdf()
            sel_course = st.multiselect("Filtrer par Cursus", courses['what_is_your_course'])
            
            query = "SELECT * FROM mental"
            if sel_course:
                formatted_courses = "', '".join(sel_course)
                query += f" WHERE what_is_your_course IN ('{formatted_courses}')"
            
            st.dataframe(con.execute(query).fetchdf(), use_container_width=True)

            # Bouton d'export des données affichées
            df_displayed = con.execute(query).fetchdf()
            download_button(df_displayed, "mental_health_export.csv", "📥 Exporter cette vue")

    else:
        st.info("Veuillez charger le fichier Santé Mentale pour activer la vue Analyse.")

# --- FOOTER GLOBAL ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {subtext_color}; font-size: 0.75rem; padding: 10px 0;">
    Data Analytics Hub · Propulsé par Streamlit, DuckDB & Plotly · Session du {st.session_state.session_start}
</div>
""", unsafe_allow_html=True)
