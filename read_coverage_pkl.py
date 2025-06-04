import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# MODIFY THIS to point to the directory that contains Beta_00, Beta_02, Beta_10.
# Example on Windows:
#   BASE_DIR = r"C:\Users\hkmufi\OneDrive - TUNI.fi\Documents\GitHub\
#               nebolab_simulator\animation_result\040625_Findrone24"
#
# Ensure that under BASE_DIR you have:
#   Beta_00\d_0\sim_data.pkl, …, Beta_00\d_9\sim_data.pkl
#   Beta_02\d_0\sim_data.pkl, …, Beta_02\d_9\sim_data.pkl
#   Beta_10\d_0\sim_data.pkl, …, Beta_10\d_9\sim_data.pkl
#
BASE_DIR = r"C:\Users\hkmufi\OneDrive - TUNI.fi\Documents\GitHub\nebolab_simulator\animation_result\040625_Findrone24"
# ─────────────────────────────────────────────────────────────────────────────

def load_coverage_from_simdata(simdata_path):
    """
    Given the full path to a sim_data.pkl file, load it via pickle
    and extract:
      - t_list   = sim_data['stored_data']['time']
      - cov_list = sim_data['stored_data']['cov_total_ratio_0']
    Returns two numpy arrays: (t_array, cov_array).
    """
    with open(simdata_path, 'rb') as f:
        sim_data = pickle.load(f)

    stored = sim_data['stored_data']
    t_list   = stored['time']
    cov_list = stored['cov_total_ratio_0']

    t_arr   = np.array(t_list,   dtype=float)
    cov_arr = np.array(cov_list, dtype=float)
    return t_arr, cov_arr

def collect_mean_coverage(beta_folder):
    """
    For a given Beta folder (e.g. BASE_DIR/Beta_00), this function:
      • Iterates over d_0, d_1, …, d_9 subfolders.
      • In each, loads sim_data.pkl and extracts (t, coverage).
      • Asserts all t‐arrays match so we can average coverage values.
      • Returns (t_common, cov_mean) as two numpy arrays.
    """
    all_t = []
    all_cov = []

    for i in range(10):
        subfolder = os.path.join(beta_folder, f"d_{i}")
        simdata_path = os.path.join(subfolder, "sim_data.pkl")
        if not os.path.isfile(simdata_path):
            raise FileNotFoundError(f"Missing file: {simdata_path}")

        t_arr, cov_arr = load_coverage_from_simdata(simdata_path)
        all_t.append(t_arr)
        all_cov.append(cov_arr)

    # Stack into arrays of shape (10, N)
    all_t   = np.stack(all_t,   axis=0)
    all_cov = np.stack(all_cov, axis=0)

    # Check all time vectors are identical
    if not np.allclose(all_t - all_t[0], 0.0):
        raise ValueError("Time vectors differ across runs; cannot average directly.")

    t_common = all_t[0]
    cov_mean = np.mean(all_cov, axis=0)
    return t_common, cov_mean

if __name__ == "__main__":
    # Names of the Beta subfolders to process
    beta_names = ["Beta_00", "Beta_02", "Beta_10"]
    # Choose distinct colors from the default matplotlib cycle
    colors = ["C0", "C1", "C2"]

    plt.figure(figsize=(8, 5))

    for idx, beta in enumerate(beta_names):
        beta_folder = os.path.join(BASE_DIR, beta)
        if not os.path.isdir(beta_folder):
            raise FileNotFoundError(f"Could not find folder: {beta_folder}")

        # Compute mean coverage vs. time for this Beta
        t_vals, cov_avg = collect_mean_coverage(beta_folder)

        plt.plot(
            t_vals,
            cov_avg,
            label=beta,
            color=colors[idx],
            linewidth=2
        )

    plt.xlabel("Time")
    plt.ylabel("Percentage of Uncovered Points$)")
    # plt.title("Mean Coverage Performance for Beta_00, Beta_02, Beta_10")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
