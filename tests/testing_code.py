

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

truc = np.random.randint(0,5,(10,2))

fig,ax = plt.subplots()
ax.plot(truc[:,0],truc[:,1])

fig.show()

