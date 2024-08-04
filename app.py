import streamlit as st
import math
from scipy.optimize import fsolve

# Définition des données du tableau
data = {
    'modèle': ['MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 'MHTC 20', 'MHTC 30', '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40',
               '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40'],
    'débit': [3.68, 4.72, 5.79, 6.98, 3.5, 5.24, 7.36, 9.44, 11.58, 13.96, 11.04, 14.16, 17.37, 20.94],
    'HMT dispo': [6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.3, 3.2, 5.5, 2.8, 6.3, 3.2, 5.5, 2.8]
    
}

# Définition des rugosités pour différents matériaux
rugosites = {
    'Cuivre': 0.0015,
    'Acier galvanisé': 0.015,
    'Acier inoxydable': 0.002,
    'Fonte': 0.26,
    'PVC': 0.0015,
    'PEHD': 0.007
}



# Fonction Colebrook-White
def colebrook(f, epsilon, D, Re):
    return 1 / math.sqrt(f) + 2 * math.log10(epsilon / (3.7 * D) + 2.51 / (Re * math.sqrt(f)))

# Fonction pour calculer les pertes de charge par mètre
def perte_charge_par_metre(f, D, v):
    g = 9.81  # Accélération due à la gravité (m/s^2)
    return f * ((v**2)/2)*(1/D) * 1000/ 10000 # Convertir en mmCE/m

# Fonction pour calculer la vitesse d'écoulement
def calculer_vitesse(Q, D):
    A = math.pi * (D / 2) ** 2  # Aire de la section transversale du tuyau
    v = Q / A
    return v

def main():
    st.title("Longueur des conduits MMTC et MHTC")
    
    # Menu déroulant pour choisir le modèle
    modèle = st.selectbox("Choisissez un modèle de PAC", data['modèle'])
    
    # Multi-choix pour les diamètres
    diamètre = st.selectbox("Choisissez un diamètre intérieur de conduit(en mm)", [33, 40, 50, 66, 80])

    # Menu déroulant pour choisir le matériau
    matériau = st.selectbox("Choisissez un matériau de conduit", list(rugosites.keys()))
    
    # Obtenir la rugosité pour le matériau sélectionné
    epsilon = rugosites[matériau] / 1000  # Convertir la rugosité en mètres

    coudes = st.selectbox("Nombre de coudes à 90° grand angle", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    dzeta_fc = st.number_input("Saisir la somme des dzettas pour filtre + clapet", min_value=0.0, step=0.1)
    
    pdc_autre = st.number_input("Saisir une valeurs de PdC supplémentaire (mCE):", min_value=0.0, step=0.1)

    # Conversion des unités
    D = diamètre / 1000  # Convertir le diamètre en mètres
    #epsilon = 0.0045 / 1000  # Convertir la rugosité en mètres

    
    # Trouver le débit correspondant au modèle choisi
    index = data['modèle'].index(modèle)
    Q_h = data['débit'][index]
    HMT_dispo = data['HMT dispo'][index]
    
    # Convertir le débit volumique de m³/h en m³/s
    Q = Q_h / 3600  # 1 heure = 3600 secondes
    
    # Calculer la vitesse d'écoulement
    v = calculer_vitesse(Q, D)
    st.write(f"La vitesse d'écoulement est: {v:.2f} m/s")


    
    # Constante de viscosité cinématique
    nu = 0.000000457  # Viscosité cinématique en m²/s
    
    # Calculer le nombre de Reynolds
    Re = (v * D) / nu
    st.write(f"Le nombre de Reynolds est: {Re:.0f}")

    #v2/2g
    y = (v**2)/(2*9.81)

    #PdC coudes 90°
    pdc_coudes = y * coudes * 0.45

    #PdC pour 2Té + 2 VI + 2 Brides
    pdc_T_VI_Br = 4.5*y

    #PdC pour filtre + clapet
    pdc_fc = y*dzeta_fc
    
    if Re > 2000:
        # Deviner une valeur initiale pour f
        initial_guess = 0.02
        
        # Utiliser fsolve pour trouver la racine de l'équation de Colebrook-White
        f_solution, = fsolve(colebrook, initial_guess, args=(epsilon, D, Re))
        
        # Calculer les pertes de charge par mètre
        perte_par_metre = perte_charge_par_metre(f_solution, D, v)
        
        # Calculer la longueur possible du tube
        longueur_possible = (HMT_dispo - pdc_coudes - pdc_T_VI_Br - pdc_fc - pdc_autre) / (perte_par_metre)  # Convertir en mètres
        
        # Afficher les résultats
        st.write(f"Le coefficient de frottement est: {f_solution:.4f}")

        #st.write(f"PdC singulières pour: 2 Té + 2 Vannes d'isolement + 2 Brides volume tampon sont: {pdc_T_VI_Br:.3f} mCE")
        st.write(f"PdC singulières totales: {pdc_coudes + pdc_T_VI_Br + pdc_fc - pdc_autre:.3f} mCE")
        st.write(f"PdCe métriques (mCE) sont: {perte_par_metre:.3f} mCE/m")

        st.write(f"La longueur possible du tube est: {math.floor(longueur_possible):.0f} mètres")
    else:
        st.write("Le régime d'écoulement est laminaire (Re <= 2000), la formule de Colebrook-White n'est pas applicable.")

if __name__ == "__main__":
    main()
