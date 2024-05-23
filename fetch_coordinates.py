import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Initialize geolocator
geolocator = Nominatim(user_agent="msa_locator")

def get_coordinates(msa_name):
    try:
        print(f"Fetching coordinates for {msa_name}...")

        # Simplify the name for better matching
        simplified_name = msa_name.split(',')[0]  # Take only the main part of the name
        location = geolocator.geocode(simplified_name)

        if location:
            print(f"Found coordinates for {simplified_name}: ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"Initial search failed for {simplified_name}. Trying fuzzy matching...")

            # Attempt fuzzy matching with variations of the name
            attempts = [
                simplified_name,
                ' '.join(simplified_name.split('-')[:-1]),  # Try without the last part after hyphen
                msa_name.split('-')[0],  # Try only the first part before hyphen
            ]

            for attempt in attempts:
                print(f"Trying with: {attempt}")
                location = geolocator.geocode(attempt)
                if location:
                    print(f"Found coordinates for {attempt}: ({location.latitude}, {location.longitude})")
                    return location.latitude, location.longitude

            print(f"All attempts failed for {msa_name}.")
            return None, None
    except GeocoderTimedOut:
        print(f"Service timed out for {msa_name}")
        return None, None
    except Exception as e:
        print(f"Error fetching coordinates for {msa_name}: {e}")
        return None, None

# Read MSA population data
msa_data = pd.read_csv('USCensus2023.csv')

# Print column names to verify
print("CSV Column Names:", msa_data.columns)

# Add new columns for latitude and longitude
msa_data['Latitude'] = None
msa_data['Longitude'] = None

# Fetch coordinates for each MSA
for idx, row in msa_data.iterrows():
    msa_name = row['MSA']
    lat, lon = get_coordinates(msa_name)
    msa_data.at[idx, 'Latitude'] = lat
    msa_data.at[idx, 'Longitude'] = lon
    time.sleep(1)  # Sleep to respect API usage limits

# Write the updated data to a new CSV
msa_data.to_csv('msa_population_with_coordinates.csv', index=False)
print("Coordinates fetched and saved to msa_population_with_coordinates.csv")
