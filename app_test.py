import streamlit as st
import math
from scipy.optimize import fsolve

# Données du tableau avec rugosité ajoutée
tubes_data = {
    "Acier": {
        "rugosites": 0.05,
        "D": {
            "1\" 1/4 (DN 32)": 35.9,
            "1\" 1/2 (DN 40)": 41.8,
            "2\" (DN 50)": 53,
            "2\" 1/2 (DN 65)": 68.8,
            "3\" (DN 80)": 80.8
        }
    },
    "Multicouches": {
        "rugosites": 0.002,
        "D": {
            "1\" 1/4 (DN 32)": 33,
            "1\" 1/2 (DN 40)": 41,
            "2\" (DN 50)": 51,
            "2\" 1/2 (DN 65)": 58,
            "3\" (DN 80)": 70
        }
    },
    "Cuivre": {
        "rugosites": 0.01,
        "D": {
            "1\" 1/4 (DN 32)": 33,
            "1\" 1/2 (DN 40)": 40,
            "2\" (DN 50)": 50,
            "2\" 1/2 (DN 65)":65,
            "3\" (DN 80)": 80
        }
    }
}





# Données de perte de charge statique pour chaque modèle MMTC
pertes_charge_statique = {
    'MMTC 20': 1.63,
    'MMTC 26': 2.04,
    'MMTC 33': 2.08,
    'MMTC 40': 1.17,
    'MHTC 20': 1.45,
    'MHTC 30': 2.55,
    '2 x MMTC 20': 1.63,
    '2 x MMTC 26': 2.04,
    '2 x MMTC 33': 2.08,
    '2 x MMTC 40': 1.17,
    '2 x MHTC 20': 1.45,
    '2 x MHTC 30': 2.55,
    '3 x MMTC 20': 1.63,
    '3 x MMTC 26': 2.04,
    '3 x MMTC 33': 2.08,
    '3 x MMTC 40': 1.17,
    '3 x MHTC 20': 1.45,
    '3 x MHTC 30': 2.55,


}

# Fonction Colebrook-White
def colebrook(f, epsilon, D, Re):
    return 1 / math.sqrt(f) + 2 * math.log10(epsilon / (3.7 * D) + 2.51 / (Re * math.sqrt(f)))

# Fonction pour calculer les pertes de charge par mètre
def perte_charge_par_metre(f, D, v):
    return f * ((v**2)/2)*(1/D) * 1000/ 10000  # Convertir en mmCE/m

# Fonction pour calculer la vitesse d'écoulement
def calculer_vitesse(Q, D):
    A = math.pi * (D / 2) ** 2  # Aire de la section transversale du tuyau
    v = Q / A
    return v

# Données pour les modèles de pompe
# data = {
#     'modèle': ['MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 'MHTC 20', 'MHTC 30', '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40',
#                '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40'],
#     'débit': [3.68, 4.72, 5.79, 6.98, 3.5, 5.24, 7.36, 9.44, 11.58, 13.96, 11.04, 14.16, 17.37, 20.94],
#     'HMT dispo': [6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.3, 3.2, 5.5, 2.8, 6.3, 3.2, 5.5, 2.8]
# }

data = {
    'modèle': ['MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 'MHTC 20', 'MHTC 30', '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40',
               '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40', '2 x MHTC 20', '2 x MHTC 30', '3 x MHTC 20', '3 x MHTC 30'],
    'débit': [3.68, 4.72, 5.79, 6.98, 3.5, 5.24, 7.36, 9.44, 11.58, 13.96, 11.04, 14.16, 17.37, 20.94, 7.0, 10.48, 10.5, 15.72],
    'HMT dispo': [6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.3, 3.2, 5.5, 2.8, 6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.4, 4.4]
}


def main():
    st.title("Longueur maximale des conduites pour PAC MMTC et MHTC")
    
    # Sélection du modèle de PAC
    st.markdown('<p style="font-size:20px; margin-bottom: 0px; margin-top: 20px;"><strong>Choisissez un modèle de PAC:</strong></p>', unsafe_allow_html=True)
    modèle = st.selectbox("", data['modèle'])

    # Sélection du matériau
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Choisissez un matériau de conduit:</strong></p>', unsafe_allow_html=True)
    materiau = st.selectbox("", list(tubes_data.keys()))

    # Sélection de la taille du tube en fonction du matériau
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Choisissez la taille du tube:</strong></p>', unsafe_allow_html=True)
    diamètre = st.selectbox("", list(tubes_data[materiau]["D"].keys()))

    # Récupérer le diamètre intérieur et la rugosité
    Diam = tubes_data[materiau]["D"][diamètre]   # Convertir en mètres
    D = Diam/1000
    rugos = tubes_data[materiau]["rugosites"]   # Convertir en mètres
    rugosites = rugos/1000
    st.write(f"Le diamètre intérieur pour le tube en {materiau}, taille {diamètre} est : {Diam} mm.")
    st.write(f"Rugosité utilisée pour le tube en {materiau} : {rugos} mm.")


    # Trouver le débit correspondant au modèle choisi
    index = data['modèle'].index(modèle)
    Q_h = data['débit'][index]
    HMT_dispo = data['HMT dispo'][index]

    # Convertir le débit volumique de m³/h en m³/s
    Q = Q_h / 3600  # 1 heure = 3600 secondes

    # Calculer la vitesse d'écoulement
    v = calculer_vitesse(Q, D)
    if v > 1.5:
        st.markdown(f"<div style='background-color: red; padding: 10px;'>La vitesse d'écoulement est de {v:.2f} m/s</div>", unsafe_allow_html=True)
    else:
        st.write(f"La vitesse d'écoulement est de {v:.2f} m/s")

    # Constante de viscosité cinématique
    nu = 0.00000131  # Viscosité cinématique en m²/s

    # Calculer le nombre de Reynolds
    Re = (v * D) / nu
    st.write(f"Le nombre de Reynolds est de {Re:.0f}")



    # Nombre de coudes à 90° grand angle

    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Nombre de coudes à 90° grand angle:</strong></p>', unsafe_allow_html=True)
    coudes = st.selectbox("", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # PdC singulières (T, VI, entrée-sortie BT)
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Somme des dzeta si connues</strong></p>', unsafe_allow_html=True)
    dzeta_T_VI_BT = st.number_input("", min_value=0.0, step=0.1)

    # PdC filtre + clapet
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>PdC de la vanne d équilibrage et autre accidents</strong></p>', unsafe_allow_html=True)
    pdc_autre = st.number_input(".", min_value=0.0, step=0.1)

    # Choix de déduire la perte de charge statique

    st.markdown('<p style="font-size:17px; margin-bottom: 0px;margin-top: 20px;"><strong>Déduire la perte de charge totale théorique pour: VI, Filtre, Clapet AR, T et Brides Tampon en fonction du modèle MMTC:</strong></p>', unsafe_allow_html=True)
    deduire_pdc_statique = st.checkbox("")

   


    Total_pdc_statique = 0

       



    # v²/2g
    y = (v**2)/(2*9.81)

    # PdC coudes 90°
    pdc_coudes = y * coudes * 0.45

    # PdC pour 2Té + 2 VI + 2 Brides
    pdc_T_VI_BT = dzeta_T_VI_BT * y

     # Si déduction de la perte de charge statique
    if deduire_pdc_statique and modèle in pertes_charge_statique:
        pdc_statique = pertes_charge_statique[modèle]
        Total_pdc_statique = pdc_coudes + pdc_T_VI_BT + pdc_statique + pdc_autre
        st.write(f"Perte de charge statique déduite : {pdc_statique} mCE")
        st.image(".\Tableau_ PdC2.png",  use_column_width=True)
        
    else:
        Total_pdc_statique = pdc_coudes + pdc_T_VI_BT + pdc_autre




    # Calculer les pertes de charge métriques et la longueur possible du tube
    if Re > 2000:
        initial_guess = 0.02
        f_solution, = fsolve(colebrook, initial_guess, args=(rugosites, D, Re))
        perte_par_metre = perte_charge_par_metre(f_solution, D, v)
        longueur_possible = (HMT_dispo - Total_pdc_statique ) / perte_par_metre

          # Afficher les résultats
        st.write(f"Le coefficient de frottement est de {f_solution:.3f}")

        #st.write(f"PdC singulières pour: 2 Té + 2 Vannes d'isolement + 2 Brides volume tampon sont: {pdc_T_VI_Br:.3f} mCE")
        st.write(f"Les PdC singulières totales sont de {Total_pdc_statique:.3f} mCE")
        st.write(f"Les PdC métriques sont de {perte_par_metre:.3f} mCE/m")

        if longueur_possible > 0:
            st.markdown(f"<div style='background-color: lightgreen; padding: 10px;'>La longueur maximale aller-retour de la conduite est de {longueur_possible:.2f} mètres</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color: red; padding: 10px;'>Les pertes de charge dépassent la HMT disponible, aucune longueur n'est possible.</div>", unsafe_allow_html=True)

    else:
        st.write("L'écoulement est laminaire, utilisez une autre méthode de calcul.")



if __name__ == "__main__":
    main()
