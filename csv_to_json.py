# csv_to_json.py
import pandas as pd

# Read the updated CSV
msa_data = pd.read_csv('msa_population_with_coordinates.csv')

# Convert to JSON
msa_data.to_json('msa_population_with_coordinates.json', orient='records')
print("Data converted to msa_population_with_coordinates.json")
