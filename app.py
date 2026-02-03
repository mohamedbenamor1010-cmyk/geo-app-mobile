import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.interpolate import PchipInterpolator

# --- CONFIGURATION INTERFACE MOBILE ---
st.set_page_config(
    page_title="Géo-Analyste Pro Mobile",
    page_icon="🏔️",
    layout="centered"
)

# Style CSS pour gros boutons tactiles et design sombre
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3.5em;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        border: None;
    }
    .stTextArea>div>div>textarea {
        background-color: #121212;
        color: #00FF00;
        font-family: 'Consolas', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏔️ Géo-Analyste Pro")
st.subheader("Analyse de Terrain - Version Mobile")

# --- 1. SOURCE IMAGE ---
st.write("📸 **Étape 1 : Charger la carte**")
file = st.file_uploader("Prendre une photo ou choisir un fichier", type=['png', 'jpg', 'jpeg'])

if file:
    img = Image.open(file)
    st.image(img, caption="Carte de travail", use_container_width=True)
    
    st.divider()

    # --- 2. PARAMÈTRES TECHNIQUES ---
    st.write("⚙️ **Étape 2 : Paramètres et Données**")
    
    with st.expander("Réglages de l'Échelle", expanded=True):
        echelle = st.number_input("Échelle (1/...) :", value=50000, step=1000)
    
    st.write("📍 **Saisie des points d'intersection**")
    st.caption("Entrez les valeurs séparées par des virgules (ex: 10, 20, 30)")
    
    col1, col2 = st.columns(2)
    with col1:
        dist_raw = st.text_area("Distances (px/mm)", "0, 150, 300, 450")
    with col2:
        alt_raw = st.text_area("Altitudes (m)", "600, 620, 640, 680")

    # --- 3. CALCULS ET RENDU ---
    if st.button("📈 TRACER LE PROFIL GÉOLOGIQUE"):
        try:
            # Nettoyage des données
            d = [float(x.strip()) for x in dist_raw.split(",") if x.strip()]
            a = [float(x.strip()) for x in alt_raw.split(",") if x.strip()]

            if len(d) != len(a):
                st.error("⚠️ Erreur : Le nombre de distances et d'altitudes doit être identique.")
            elif len(d) < 3:
                st.warning("⚠️ Précision : Ajoutez au moins 3 points pour un profil fluide.")
            else:
                # Moteur de calcul (Ratio 40px = 1cm)
                x_km = np.array([(val / 40 * echelle) / 100000 for val in d])
                y_m = np.array(a)

                # Interpolation PCHIP (Standard Géologique)
                x_grid = np.linspace(x_km.min(), x_km.max(), 600)
                interp_func = PchipInterpolator(x_km, y_m)
                y_smooth = interp_func(x_grid)

                # Création du Graphique
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x_grid, y_smooth, color='#4E342E', linewidth=3, label="Topographie")
                ax.fill_between(x_grid, y_smooth, color='#8D6E63', alpha=0.3)

                # OPTIMISATION SCIENTIFIQUE (AXE Y)
                ax.set_ylim(min(y_m) - 25, max(y_m) + 50)

                # Habillage
                ax.set_xlabel("Distance cumulée (km)", fontweight='bold')
                ax.set_ylabel("Altitude (m)", fontweight='bold')
                ax.set_title(f"Coupe Topographique (1/{echelle})", fontsize=14)
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.legend()

                st.pyplot(fig)
                st.success("✅ Analyse terminée avec succès !")

        except Exception as e:
            st.error(f"❌ Erreur : {e}")

st.divider()
st.caption("Géo-Analyste Pro v18.5 | Optimisé pour le terrain")
