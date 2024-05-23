from flask import Flask, render_template, request
import pandas as pd
import folium
import random

app = Flask(__name__)

# Load the cleaned dataset
msa_data = pd.read_csv('msa_population_with_coordinates.csv')

def calculate_demand_score(population_1, population_2, distance):
    # Remove commas and convert populations to integers
    population_1 = int(population_1.replace(',', ''))
    population_2 = int(population_2.replace(',', ''))

    # Gravity model constants
    alpha = 0.000000002
    beta = 2

    # Calculate the demand score
    demand_score = alpha * population_1 * population_2 / (distance ** beta)
    return demand_score


def create_map():
    # Create a map centered in the US
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

    # Add markers for each MSA
    for _, row in msa_data.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):  # Check if latitude and longitude are not NaN
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['MSA']} - Population: {row['Population']}",
                tooltip=row['MSA']
            ).add_to(m)

    return m

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get selected MSAs
        msa1 = request.form.get('msa1')
        msa2 = request.form.get('msa2')

        # Retrieve data for selected MSAs
        msa_data_1 = msa_data[msa_data['MSA'] == msa1].iloc[0]
        msa_data_2 = msa_data[msa_data['MSA'] == msa2].iloc[0]

        # Calculate distance (for simplicity, we'll use Euclidean distance)
        distance = ((msa_data_1['Latitude'] - msa_data_2['Latitude']) ** 2 +
                    (msa_data_1['Longitude'] - msa_data_2['Longitude']) ** 2) ** 0.5

        # Calculate demand score
        demand_score = calculate_demand_score(msa_data_1['Population'], msa_data_2['Population'], distance)

        # Generate random color for the line
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # Render the map with the line between the selected points
        m = create_map()
        folium.PolyLine(locations=[[msa_data_1['Latitude'], msa_data_1['Longitude']],
                                    [msa_data_2['Latitude'], msa_data_2['Longitude']]],
                        color=color,
                        weight=demand_score/1000,  # Adjust line thickness based on demand score
                        popup=f"Demand Score: {demand_score:.2f}",
                        tooltip=f"Demand Score: {demand_score:.2f}"
                        ).add_to(m)
        map_html = m._repr_html_()

        return render_template('map.html', map_html=map_html, msa_data=msa_data, msa1=msa1, msa2=msa2)

    else:
        # Create the map without the line
        m = create_map()
        map_html = m._repr_html_()
        return render_template('map.html', map_html=map_html, msa_data=msa_data)

if __name__ == '__main__':
    app.run(debug=True)
