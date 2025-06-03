# This script processes the assignment position data from the Findrone simulation results.

import json
import numpy as np
import matplotlib.pyplot as plt
import os

# Load the json DATA
file_path = r"C:\Users\hkmufi\Downloads\simulation_results.json"
with open(file_path, 'r') as file:
    data = json.load(file)

cluster_key = "[117.5, 87.5, 119.0]"
sensing_key = "[8, 7, 9, 13, 5, 11, 13, 13, 10, 11]"

# Extract iterations
iterations = data['simulations'][cluster_key][sensing_key][0]['iterations']

# Determine number of clusters and items from the first assignment matrix
first_matrix = np.array(iterations[0]["results"][0]["assignment_matrix"])
num_items, num_clusters = first_matrix.shape

# Define betas and initialize the counts array
betas = [0.0, 0.5, 1.0]
counts = np.zeros((len(betas), num_clusters, num_items), dtype=int)

# Aggregate counts for each beta accross iterations 0-49
for it in iterations:
    if it["iteration"] < 50:
        for res in it["results"]:
            beta_index = betas.index(res["alpha"])
            matrix = np.array(res["assignment_matrix"])
            counts[beta_index] += (matrix > 0).astype(int).T

# Compute global vmin, vmax for color scaling
vmin, vmax = counts.min(), counts.max()

# Plot small multiples heatmap for each beta with uniform color scaling
fig, axes = plt.subplots(len(betas), 1, figsize=(10, 6), dpi=100, sharex=True)

for idx, beta in enumerate(betas):
    ax = axes[idx]
    im = ax.imshow(counts[idx], aspect='auto', cmap='GnBu', vmin=vmin, vmax=vmax)
    for i in range(num_clusters):
        for j in range(num_items):
            val = counts[idx, i, j]
            text_color = 'white' if val > (vmax + vmin) / 2 else 'black'
            ax.text(j, i, str(val), ha='center', va='center', color=text_color)
    ax.set_yticks(range(num_clusters))
    ax.set_yticklabels([f'$\\ell_{i+1}$' for i in range(num_clusters)], fontsize=14)
    ax.set_title(r'$\beta = {}$'.format(beta), pad=10, fontsize=14)
    if idx == len(betas) - 1:
        ax.set_xticks(np.arange(num_items))
        ax.set_xticklabels(np.arange(1, num_items + 1))
        ax.set_xlabel('Drones', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(file_path), 'assignment_heatmaps.pdf'), dpi=300)
plt.show()
