import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import random
import hashlib
import time
from perlin_noise import PerlinNoise
from tqdm import tqdm

def generate_voxel_landscape(size=30, height_factor=10, octaves=3, seed=None):
    """
    Génère un paysage en voxels avec du bruit de Perlin pour un terrain naturel.
    
    Args:
        size: Taille du terrain (size x size voxels)
        height_factor: Facteur d'amplification de la hauteur
        octaves: Nombre d'octaves pour le bruit de Perlin (plus = plus détaillé)
        seed: Graine pour la génération aléatoire
        
    Returns:
        Un tableau numpy 3D représentant le paysage en voxels
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Création du générateur de bruit de Perlin
    noise = PerlinNoise(octaves=octaves, seed=seed)
    
    # Génération du terrain de base avec du bruit de Perlin
    terrain = np.zeros((size, size))
    
    # Utilisation de tqdm pour montrer la progression
    print("Génération du terrain de base...")
    for i in tqdm(range(size), desc="Création du terrain", ncols=100):
        for j in range(size):
            # Normalisation des coordonnées entre 0 et 1
            nx, ny = i/size, j/size
            # Génération de la hauteur avec le bruit de Perlin
            terrain[i, j] = noise([nx, ny])
    
    # Normalisation et mise à l'échelle du terrain
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    terrain = np.floor(terrain * height_factor).astype(int)
    
    # Création du tableau 3D pour les voxels
    voxels = np.zeros((size, size, int(terrain.max()) + 1), dtype=bool)
    
    # Remplissage des voxels
    print("Remplissage des voxels...")
    for i in tqdm(range(size), desc="Construction des voxels", ncols=100):
        for j in range(size):
            height = int(terrain[i, j])
            voxels[i, j, :height+1] = True
    
    return voxels, terrain

def create_color_map(terrain, size, water_level=0.3):
    """
    Crée une carte de couleurs pour le paysage.
    
    Args:
        terrain: Le terrain 2D
        size: Taille du terrain
        water_level: Niveau d'eau (proportion de la hauteur max)
        
    Returns:
        Un tableau numpy 3D représentant les couleurs des voxels
    """
    # Hauteur maximale du terrain
    max_height = terrain.max()
    
    # Niveau d'eau
    water_height = int(max_height * water_level)
    
    # Couleurs pour les différentes zones (eau, plage, plaine, forêt, montagne, neige)
    water_color = [0.0, 0.4, 0.8, 0.8]  # Bleu
    beach_color = [0.9, 0.8, 0.6, 1.0]  # Beige
    plain_color = [0.4, 0.8, 0.4, 1.0]  # Vert clair
    forest_color = [0.0, 0.5, 0.2, 1.0]  # Vert foncé
    mountain_color = [0.5, 0.5, 0.5, 1.0]  # Gris
    snow_color = [1.0, 1.0, 1.0, 1.0]  # Blanc
    
    # Initialisation de la carte de couleurs
    colors = np.zeros((size, size, int(max_height) + 1, 4))
    
    # Utilisation de tqdm pour montrer la progression
    print("Application des couleurs...")
    for i in tqdm(range(size), desc="Coloration du paysage", ncols=100):
        for j in range(size):
            height = int(terrain[i, j])
            
            # Coloration en fonction de la hauteur
            for k in range(height + 1):
                if k <= water_height:
                    colors[i, j, k] = water_color
                elif k <= water_height + 1:
                    colors[i, j, k] = beach_color
                elif k <= max_height * 0.4:
                    colors[i, j, k] = plain_color
                elif k <= max_height * 0.6:
                    colors[i, j, k] = forest_color
                elif k <= max_height * 0.8:
                    colors[i, j, k] = mountain_color
                else:
                    colors[i, j, k] = snow_color
    
    return colors

def visualize_voxel_landscape(voxels, colors, size, filename='voxel_landscape.png'):
    """
    Visualise le paysage en voxels avec Matplotlib.
    
    Args:
        voxels: Tableau 3D des voxels
        colors: Tableau 3D des couleurs
        size: Taille du terrain
        filename: Nom du fichier pour enregistrer l'image
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Affichage des voxels avec leurs couleurs
    ax.voxels(voxels, facecolors=colors, edgecolor='k', linewidth=0.1)
    
    # Configuration de la vue
    ax.view_init(elev=30, azim=45)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Paysage en voxels')
    
    # Équilibrer les axes pour que les voxels soient cubiques
    max_range = max(size, voxels.shape[2])
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_zlim(0, voxels.shape[2])
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    #plt.show()

def generate_unique_id(size, height_factor, octaves, seed, water_level):
    """
    Génère un identifiant unique pour l'image basé sur les paramètres et un aléa.
    
    Args:
        size: Taille du terrain
        height_factor: Facteur de hauteur
        octaves: Nombre d'octaves
        seed: Graine pour la génération
        water_level: Niveau d'eau
        
    Returns:
        Une chaîne de caractères représentant l'identifiant unique
    """
    import hashlib
    import time
    
    # Génération d'un aléa basé sur le temps actuel
    random_component = str(time.time())
    
    # Création d'une chaîne contenant tous les paramètres
    params_str = f"size={size}_height={height_factor}_octaves={octaves}_seed={seed}_water={water_level}_{random_component}"
    
    # Génération d'un hash SHA-256 pour créer un ID court mais unique
    unique_id = hashlib.sha256(params_str.encode('utf-8')).hexdigest()[:12]
    
    return unique_id

def main():
    # Paramètres
    size = 100  # Taille du terrain (plus petit pour un rendu plus rapide)
    height_factor = 50  # Facteur de hauteur
    octaves = 5  # Détail du terrain
    seed = random.randint(0, 1000)  # Graine aléatoire
    water_level = 0.2  # Niveau d'eau relatif
    
    # Génération de l'identifiant unique
    unique_id = generate_unique_id(size, height_factor, octaves, seed, water_level)
    filename = f"voxel_landscape_{unique_id}.png"
    
    print(f"Génération d'un paysage en voxels (seed: {seed}, ID: {unique_id})...")
    
    # Génération du terrain
    voxels, terrain = generate_voxel_landscape(size, height_factor, octaves, seed)
    
    # Création de la carte de couleurs
    colors = create_color_map(terrain, size, water_level)
    
    # Visualisation
    print("Visualisation du paysage...")
    visualize_voxel_landscape(voxels, colors, size, filename)
    
    print(f"Terminé ! L'image a été enregistrée sous '{filename}'")
    print(f"Paramètres utilisés: size={size}, height_factor={height_factor}, octaves={octaves}, seed={seed}, water_level={water_level}")

if __name__ == "__main__":
    main()
