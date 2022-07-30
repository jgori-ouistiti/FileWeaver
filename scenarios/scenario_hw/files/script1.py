import os

for link in ["https://scikit-learn.org/stable/_images/sphx_glr_plot_pca_vs_lda_001.png"
            ,"https://scikit-learn.org/stable/_images/sphx_glr_plot_pca_vs_lda_002.png"]:
    os.system(f"wget -P fig {link} -nc -q")
    
for adj in ["Good","Bad"]:
    os.system(f"cp ../src/{adj}ConfusionMatrix.png fig/{adj}.png")
