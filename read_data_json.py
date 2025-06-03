import json
import os
import pandas as pd
from collections import defaultdict

def calculate_cluster_ratios(matrix, cluster_sizes):
    """Calculate the ratio for each cluster: sum of non-zero values in column / cluster size."""
    if not matrix or not cluster_sizes:
        return [0.0] * len(cluster_sizes)
    ratios = []
    for col_idx in range(len(cluster_sizes)):
        col_sum = sum(row[col_idx] for row in matrix if row[col_idx] != 0.0)
        ratio = col_sum / cluster_sizes[col_idx] if cluster_sizes[col_idx] != 0 else 0.0
        ratios.append(ratio)
    return ratios

def calculate_total_ratio(matrix, cluster_sizes):
    """Calculate the total ratio: sum of all non-zero values / sum of cluster sizes."""
    if not matrix or not cluster_sizes:
        return 0.0
    total_sum = sum(value for row in matrix for value in row if value != 0.0)
    total_cluster_size = sum(cluster_sizes)
    return total_sum / total_cluster_size if total_cluster_size != 0 else 0.0

def compare_metrics(json_file_path, tolerance=0.0001, output_excel_name="simulation_results_output.xlsx"):
    # Get the directory of the JSON file
    json_dir = os.path.dirname(json_file_path) if os.path.dirname(json_file_path) else '.'
    # Construct the full path for the Excel file
    output_excel = os.path.join(json_dir, output_excel_name)
    
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Dictionary to store results
    results = defaultdict(list)
    
    # Navigate through the simulations
    simulations = data.get('simulations', {})
    for cluster_size_str, cluster_data in simulations.items():
        # Convert cluster_size string to list of floats
        cluster_size = [float(x) for x in cluster_size_str.strip('[]').split(',')]
        num_clusters = len(cluster_size)
        
        for sensing_range, trials in cluster_data.items():
            for trial in trials:
                for iteration in trial.get('iterations', []):
                    iteration_num = iteration['iteration']
                    sensing_range = iteration.get('sensing_range', [])
                    metrics = {'alpha_0': {}, 'alpha_1': {}}
                    
                    # Extract metrics, assignment_matrix, and execution_time for alpha 0.0 and 1.0
                    for result in iteration.get('results', []):
                        alpha = result['alpha']
                        if alpha == 0.0:
                            metrics['alpha_0'] = {
                                'metric_1': result['metric_1'],
                                'metric_2': result['metric_2'],
                                'assignment_matrix': result['assignment_matrix'],
                                'execution_time': result['execution_time']
                            }
                        elif alpha == 1.0:
                            metrics['alpha_1'] = {
                                'metric_1': result['metric_1'],
                                'metric_2': result['metric_2'],
                                'assignment_matrix': result['assignment_matrix'],
                                'execution_time': result['execution_time']
                            }
                    
                    # Compare metrics with tolerance
                    flag_1 = 0
                    flag_2 = 0
                    if metrics['alpha_0'] and metrics['alpha_1']:
                        diff_metric_1 = abs(metrics['alpha_0']['metric_1'] - metrics['alpha_1']['metric_1'])
                        diff_metric_2 = abs(metrics['alpha_0']['metric_2'] - metrics['alpha_1']['metric_2'])
                        if diff_metric_1 > tolerance:
                            flag_1 = 1
                        if diff_metric_2 > tolerance:
                            flag_2 = 1
                    
                    # Calculate cluster and total ratios
                    cluster_ratios_alpha_0 = calculate_cluster_ratios(
                        metrics['alpha_0'].get('assignment_matrix', None), cluster_size
                    )
                    cluster_ratios_alpha_1 = calculate_cluster_ratios(
                        metrics['alpha_1'].get('assignment_matrix', None), cluster_size
                    )
                    total_ratio_alpha_0 = calculate_total_ratio(
                        metrics['alpha_0'].get('assignment_matrix', None), cluster_size
                    )
                    total_ratio_alpha_1 = calculate_total_ratio(
                        metrics['alpha_1'].get('assignment_matrix', None), cluster_size
                    )
                    
                    # Store result, formatting metric_2 to 10 decimal places
                    result = {
                        'iteration': iteration_num,
                        'sensing_range': sensing_range,
                        'flag_1': flag_1,
                        'flag_2': flag_2,
                        'metric_1_alpha_0': metrics['alpha_0'].get('metric_1', None),
                        'metric_1_alpha_1': metrics['alpha_1'].get('metric_1', None),
                        'metric_2_alpha_0': metrics['alpha_0'].get('metric_2', None),
                        'metric_2_alpha_1': metrics['alpha_1'].get('metric_2', None),
                        'execution_time_alpha_0': metrics['alpha_0'].get('execution_time', None),
                        'execution_time_alpha_1': metrics['alpha_1'].get('execution_time', None),
                        'assignment_matrix_alpha_0': metrics['alpha_0'].get('assignment_matrix', None),
                        'assignment_matrix_alpha_1': metrics['alpha_1'].get('assignment_matrix', None),
                        'total_ratio_alpha_0': total_ratio_alpha_0,
                        'total_ratio_alpha_1': total_ratio_alpha_1
                    }
                    # Add individual cluster ratios
                    for i in range(num_clusters):
                        result[f'Alpha_0_Cluster_{i+1}'] = cluster_ratios_alpha_0[i] if i < len(cluster_ratios_alpha_0) else 0.0
                        result[f'Alpha_1_Cluster_{i+1}'] = cluster_ratios_alpha_1[i] if i < len(cluster_ratios_alpha_1) else 0.0
                    
                    results[cluster_size_str].append(result)
    
    # Prepare data for Excel
    excel_data = []
    for cluster_size, iterations in results.items():
        for res in sorted(iterations, key=lambda x: x['iteration']):
            # Convert cluster_size string to list to determine number of clusters
            cluster_size_list = [float(x) for x in cluster_size.strip('[]').split(',')]
            num_clusters = len(cluster_size_list)
            
            # Convert assignment matrices to string for Excel
            matrix_0_str = str(res['assignment_matrix_alpha_0']) if res['assignment_matrix_alpha_0'] else ''
            matrix_1_str = str(res['assignment_matrix_alpha_1']) if res['assignment_matrix_alpha_1'] else ''
            # Format metric_2 to 10 decimal places for Excel
            metric_2_alpha_0 = f"{res['metric_2_alpha_0']:.10f}" if res['metric_2_alpha_0'] is not None else ''
            metric_2_alpha_1 = f"{res['metric_2_alpha_1']:.10f}" if res['metric_2_alpha_1'] is not None else ''
            # Format total ratios to 4 decimal places with comma
            total_ratio_alpha_0 = f"{res['total_ratio_alpha_0']:.4f}".replace('.', ',') if res['total_ratio_alpha_0'] is not None else ''
            total_ratio_alpha_1 = f"{res['total_ratio_alpha_1']:.4f}".replace('.', ',') if res['total_ratio_alpha_1'] is not None else ''
            
            # Create Excel row
            row = {
                'Cluster_Size': cluster_size,
                'Iteration': res['iteration'],
                'Sensing_Range': str(res['sensing_range']),
                'Flag_1_Metric_1': res['flag_1'],
                'Flag_2_Metric_2': res['flag_2'],
                'Metric_1_Alpha_0': res['metric_1_alpha_0'],
                'Metric_1_Alpha_1': res['metric_1_alpha_1'],
                'Metric_2_Alpha_0': metric_2_alpha_0,
                'Metric_2_Alpha_1': metric_2_alpha_1,
                'Execution_Time_Alpha_0': res['execution_time_alpha_0'],
                'Execution_Time_Alpha_1': res['execution_time_alpha_1'],
                'Assignment_Matrix_Alpha_0': matrix_0_str,
                'Assignment_Matrix_Alpha_1': matrix_1_str,
                'Assignment_Matrix_Total_Ratio_Alpha_0': total_ratio_alpha_0,
                'Assignment_Matrix_Total_Ratio_Alpha_1': total_ratio_alpha_1
            }
            # Add individual cluster ratio columns with comma
            for i in range(num_clusters):
                row[f'Alpha_0_Cluster_{i+1}'] = f"{res[f'Alpha_0_Cluster_{i+1}']:.4f}".replace('.', ',')
                row[f'Alpha_1_Cluster_{i+1}'] = f"{res[f'Alpha_1_Cluster_{i+1}']:.4f}".replace('.', ',')
            
            excel_data.append(row)
    
    # Write to Excel
    df = pd.DataFrame(excel_data)
    df.to_excel(output_excel, index=False, engine='openpyxl')
    
    # Print results to console
    for cluster_size, iterations in results.items():
        print(f"\nCluster Size: {cluster_size}")
        print(f"Total iterations: {len(iterations)}")
        for res in sorted(iterations, key=lambda x: x['iteration']):
            print(f"\nIteration {res['iteration']}:")
            print(f"Sensing Range: {res['sensing_range']}")
            print(f"Flag_1 (Metric_1) = {res['flag_1']}, Flag_2 (Metric_2) = {res['flag_2']}")
            print(f"Metric_1 (Alpha 0: {res['metric_1_alpha_0']}, Alpha 1: {res['metric_1_alpha_1']})")
            # Format metric_2 to 10 decimal places for console
            metric_2_alpha_0_display = f"{res['metric_2_alpha_0']:.10f}" if res['metric_2_alpha_0'] is not None else 'None'
            metric_2_alpha_1_display = f"{res['metric_2_alpha_1']:.10f}" if res['metric_2_alpha_1'] is not None else 'None'
            print(f"Metric_2 (Alpha 0: {metric_2_alpha_0_display}, Alpha 1: {metric_2_alpha_1_display})")
            print("Assignment Matrix (Alpha 0):")
            if res['assignment_matrix_alpha_0']:
                for row in res['assignment_matrix_alpha_0']:
                    print(row)
            print("Assignment Matrix (Alpha 1):")
            if res['assignment_matrix_alpha_1']:
                for row in res['assignment_matrix_alpha_1']:
                    print(row)
        print(f"\nNumber of Metric_1 conflicts: {sum(res['flag_1'] for res in iterations)}")
        print(f"Number of Metric_2 conflicts: {sum(res['flag_2'] for res in iterations)}")
    print(f"\nResults saved to {output_excel}")

if __name__ == "__main__":
    json_file_path = "C:\\Users\\hkmufi\\Downloads\\findrone_simulation_results.json"
    compare_metrics(json_file_path, output_excel_name="findrone_simulation_results_output.xlsx")
