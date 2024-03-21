import streamlit as st
import os
import time
import re
import numpy as np
import pandas as pd 
import subprocess
import matplotlib.pyplot as plt
import sys
import torch
sys.path.append('sub_code/')  # Add the directory containing 'NEDO_user_code.py' to the Python path
import NEDO_original


# Set page title and icon
st.set_page_config(
    page_title="Piste de réflexions",
    page_icon="🔬",
)

# Main title
st.title("🔬 Piste de réflexions")

# Create a sidebar for navigation
page = st.sidebar.radio("Aller à", ["NEDOS", "Latent ODE", "Normalizing Flow"])

# Define the content for each page
if page == "NEDOS":
    st.markdown("<h1 style='text-align: center; color: white;'>Neural ODEs", unsafe_allow_html=True)

    st.write(r"""En guise de preuve de concept, nous allons maintenant tester si un ODE neuronal peut effectivement restaurer la vraie fonction de dynamique à l'aide de données échantillonnées. Pour ce faire, nous spécifierons un ODE, le ferons évoluer et échantillonnerons des points sur sa trajectoire, puis le restaurerons. 
         Tout d'abord, nous testerons un ODE linéaire simple. 
         La dynamique est donnée la matrice ci dessous matrice.
$$
\frac{dz}{dt} = \begin{bmatrix}-0.1 & -1.0\\1.0 & -0.1\end{bmatrix} z
$$

Pour l'implémentation, nous utiliserons un module de réseau de neurones linéaires avec une couche d'entrée de dimension 2 
et une couche de sortie de dimension 2, sans biais (```nn.Linear(2, 2, bias=False)```).
         """)

    
    # Function to read PNG files corresponding to each iteration
    def read_png_files(folder_path):
        png_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')], key=sort_key)
        return png_files

    # Custom sorting function to sort filenames based on their numeric part
    def sort_key(filename):
        return int(re.search(r'\d+', filename).group())

    # Graph plot function
    def plot_graph_example():
        st.title('Evolution de votre résultat')

        # Start button to initiate the animation
        if st.button("Commencer l'animation", key="start_animation"):
            # Select folder containing PNG files
            folder_path = "data/dim2.1"
            st.empty()  # Placeholder for the slider

            # Check if folder path is provided
            if folder_path:
                # Read PNG files from the folder
                png_files = read_png_files(folder_path)

                # Placeholder for the selected image
                selected_image_placeholder = st.empty()

                # Progress through the iterations automatically
                for i in range(len(png_files) * 10):  # Progress through each step of 10
                    time.sleep(0.01)  # Adjust the speed of progression
                    iteration = i // 10 * 10  # Get the current iteration

                    # Display the selected PNG file
                    selected_png = os.path.join(folder_path, png_files[iteration // 10])
                    selected_image_placeholder.image(selected_png, use_column_width=True)

                # Button to restart the progress
                restart_button = st.button("Recommencer l'animation", key="restart_button")
                if restart_button:
                    start_progress = True  # Set the flag to start progress again
                
    def plot_graph_user():
        st.title('Evolution du résultat')

        # Start button to initiate the animation
        if st.button("Commencer l'animation", key="start_user_animation"):
            # Select folder containing PNG files
            folder_path = "data/user_try"
            st.empty()  # Placeholder for the slider

            # Check if folder path is provided
            if folder_path:
                # Read PNG files from the folder
                png_files = read_png_files(folder_path)

                # Placeholder for the selected image
                selected_image_placeholder = st.empty()

                # Progress through the iterations automatically
                for i in range(len(png_files) * 10):  # Progress through each step of 50 to be faster
                    time.sleep(0.0000001)  # Adjust the speed of progression
                    iteration = i // 10 * 10  # Get the current iteration

                    # Display the selected PNG file
                    selected_png = os.path.join(folder_path, png_files[iteration // 10])
                    selected_image_placeholder.image(selected_png, use_column_width=True)

                # Button to restart the progress
                restart_button = st.button("Recommencer l'animation", key="restart_button")
                if restart_button:
                    start_progress = True  # Set the flag to start progress again
                
    def create_matrix():
        st.title("À votre tour !")
        st.write(r"""Essayez de résoudre votre équation différentielle dans $\mathbb{R}^{2}$ avec un NODE. 
             Nous restons dans le cadre d'une équation différencielle *linéaire* pour simplifier le modèle.""")
        st.write(r"""C'est à dire un problème de la forme 
             $$\frac{dz}{dt} = Az$$ avec $A \in \mathcal{M}_{2}(\mathbb{R})$.""")


        st.write(r"""Commencez par entrer votre matrice $A$.""")

        matrix = [[0,0], [0,0]]
        value_00 = float(st.number_input(f"Ligne 1, Colonne 1", key = "00"))
        matrix[0][0] = value_00
        value_01 = float(st.number_input(f"Ligne 1, Colonne 2", key = "01"))
        matrix[0][1] = value_01
        value_10 = float(st.number_input(f"Ligne 2, Colonne 1", key = "10"))
        matrix[1][0] = value_10
        value_11 = float(st.number_input(f"Ligne 2, Colonne 2", key = "11"))
        matrix[1][1] = value_11

        print(type(matrix))
        
        return matrix
    
    def matrix_to_torch(matrix):
        
        if st.button("Enregistrer la matrice", key = "save_torch_matrix"):
            
            #Converting Matrix to torch
            matrix = torch.tensor(matrix)
            #matrix = matrix.clone().detach()
            #matrix.requires_grad_(True)
            
            #Saving for call later
            torch.save(matrix, 'data/matrix.pth')
        
    def show_matrix(matrix):
        
        st.write("Votre matrice A en input vérifie l'EDO suivante :")
        nice_matrix = np.zeros((2,2))
        
        nice_matrix[0,0] = matrix[0][0]
        nice_matrix[0,1] = matrix[0][1]
        nice_matrix[1,0] = matrix[1][0]
        nice_matrix[1,1] = matrix[1][1]

        # Convert the matrix to a LaTeX string
        
        latex_matrix = r"\begin{bmatrix}"
        for row in nice_matrix:
            for value in row:
                latex_matrix += f"{value} & "
            latex_matrix = latex_matrix[:-2]  # Remove the last '& ' from each row
            latex_matrix += r"\\"
        latex_matrix += r"\end{bmatrix}"
        
        # Display the LaTeX equation
        st.latex(fr"\frac{{dz}}{{dt}} = {latex_matrix} z")
            
    def check_conditions(A):
        st.write("Il est commode de vérifier les conditions de stabilité de la matrice en input pour un meilleur résultat numérique.")
        # Stability: Check if real parts of eigenvalues are negative
        eigenvalues, _ = np.linalg.eig(A)
        is_stable = np.all(np.real(eigenvalues) <= 0)
        
        if is_stable:
            st.write("Les parties réelles des valeurs propres sont négatives. ✅")
        else:
            st.write(f"Les parties réelles des valeurs propres ({eigenvalues}) sont positives. ❌")

        # Non-degeneracy: Check if matrix is non-singular
        is_nonsingular = np.linalg.det(A) != 0
        if is_nonsingular:
            st.write("La matrice est non dégénérée. ✅")
        else:
            st.write("La matrice est dégénérée. ❌")

        # Real Eigenvalues: Check if eigenvalues are real
        is_real_eigenvalues = np.all(np.imag(eigenvalues) == 0)
        if is_real_eigenvalues:
            st.write("Les valeurs propres de la matrice sont réelles. ✅")
        else:
            st.write("Les valeurs propres de la matrice ne sont pas réelles. ✅")

    def choose_parameters():
        st.write(r""" Le point clef de la méthoden NODE est qu'il repose sur la méthode de l'adjoint pour calculer $\nabla_{\theta}L$. 
                 Ceci implique donc directement l'utilisation d'une fonction $L$ différentiable, ou au moins dérivable. 
                 Pour appliquer la méthode NODE, vous avez le choix entre plusieurs fonctions de loss ainsi que le choix du nombre d'itérations.
                 Nous recommandons au moins 1000 itérations : l'algorithme peut prendre du temps à converger.
                 """)

        # Define loss function choices with keys
        loss_function_choices = {
            "Mean Squared Error (MSE)": "F.mse_loss",
            "Mean Absolute Error (MAE)": "F.l1_Loss",
            "Huber Loss (HL)": "F.HuberLoss",
            "Log-Cosh Loss (LGL)": "log_cosh"
        }

        # Prompt the user to choose a loss function
        loss_function_choice = st.selectbox(
            "Choose a loss function:",
            options=list(loss_function_choices.keys()),
            key="loss_function_choice"
        )

        # Get the key corresponding to the selected loss function
        selected_key = loss_function_choices[loss_function_choice]
        
        # Open a file in write mode
        with open("data/loss_function.py", "w") as file:
        # Write the integer value as a Python variable assignment
            file.write("import torch\n")
            file.write("from torch.nn import functional as F\n")
            file.write(f"user_loss = {str(selected_key)}")
            
        # Prompt the user to enter the number of iterations
        iterations = st.number_input("Enter the number of iterations:", min_value=1, step=1)
        
        # Open a file in write mode
        with open("data/iteration.py", "w") as file:
        # Write the integer value as a Python variable assignment
            file.write(f"user_it = {int(iterations)}")
        
        # Return the chosen loss function key and number of iterations
        return selected_key, iterations
    
    
    def try_code():
        # Button to run the code
        if st.button("Essayer le code soit même", key = "code"):
            
            # Execute the code
             NEDO_original.main()


    def main():
        start_progress = False 
        plot_graph_example()
        matrix = create_matrix()
        show_matrix(matrix)
        check_conditions(matrix)
        matrix_to_torch(matrix)
        loss_function_key, iterations = choose_parameters()
        try_code()
        plot_graph_user()
        
    if __name__ == '__main__':
        main()

elif page == "Latent ODE":
    #Noor
    st.write("This is the content of Latent 0DE")
    
    
elif page == "Normalizing Flow":
    #Malek

    st.write("This is the content of Normalizing Flow")

    st.write("Nous allons étudier de code")
