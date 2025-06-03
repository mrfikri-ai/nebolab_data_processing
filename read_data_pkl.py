import os
import pickle
import pandas as pd

def process_allocation_files(root_dir, output_xlsx_path):
    """
    Walk through directories under root_dir, find ACO_allocation.pkl files,
    extract relevant data, compute densities and ratios, and save to an Excel file.

    Arguments:
    root_dir (str): The root directory to search for ACO_allocation.pkl files.
    output_xlsx_path (str): Path where the resulting Excel file will be saved.
    """
    rows = []
    for current_root, dirs, files in os.walk(root_dir):
        if 'ACO_allocation.pkl' in files:
            d_folder = os.path.basename(current_root)
            with open(os.path.join(current_root, 'ACO_allocation.pkl'), 'rb') as f:
                data = pickle.load(f)
            sr_area, dict_centroid, dict_dividedPoints, dict_bbox, chosenAgentIdx, dict_task_area = data

            for area_id, points in dict_dividedPoints.items():
                count = points.shape[0]
                area_size = dict_task_area[area_id]
                density = count / area_size if area_size != 0 else None

                agents = chosenAgentIdx.get(area_id, [])
                sensing_sum = sum(sr_area[i] for i in agents)
                ratio = sensing_sum / area_size if area_size != 0 else None

                rows.append({
                    'd_folder': d_folder,
                    'area_id': area_id,
                    'broken_sensor_count': count,
                    'area_size': area_size,
                    'density': density,
                    'sensing_area_sum': sensing_sum,
                    'sensing_to_task_area_ratio': ratio,
                    'allocated_agents': agents,
                    # 'divided_points': points,      # Uncomment if you need raw point data
                    # 'bounding_box': dict_bbox.get(area_id),  # Uncomment if you need bounding box
                })

    df = pd.DataFrame(rows)
    df.to_excel(output_xlsx_path, index=False)
    return df

# Usage with the specified directories:
# Take the data from the folder
root_directory = r""
# Save the data into xlsx file
output_path = r"allocation_summary.xlsx"

# Generate the Excel file
df_summary = process_allocation_files(root_directory, output_path)
print("Saved allocation summary to:", output_path)
