import json
import pandas as pd

# Omschrijvingen tabel inlezen
rel_path = 'location_description_map.json'
with open(rel_path, 'r') as r:
    description_data = json.load(r)

# Df for the connection between the sbs/lbs numbers and their description
description_df = pd.DataFrame(description_data)
