import earthaccess
import h5py
import he5_to_json
import re
import os
import numpy as np
import json

# Use these as environment variables with your own login credentials
# EARTHDATA_USERNAME="Add_your_USERNAME_in_your_environment"
# EARTHDATA_PASSWORD="Add_your_PASSWORD_in_your_environment"
earthaccess.login(strategy="environment")

HE5_DATA_FOLDER ="./data2"

print("#########################################################")
print("#########################################################")

concept_ids = []

def find_concept_ids(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            if key.lower() == "concept-id":
                # print(f"Found concept-id at {new_path}: {value}")
                concept_ids.append(value)
            find_concept_ids(value, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_concept_ids(item, f"{path}[{i}]")
    elif hasattr(obj, "__dict__"):
        find_concept_ids(vars(obj), path)

def remove_duplicates(lst):
    return list(dict.fromkeys(lst))

def fetch_dataset(satellite_key):
    # fetch all the concept IDs
    datasets = earthaccess.search_datasets(
        keyword=satellite_key,
        cloud_hosted=True,
        count=100
    )

    for data in datasets:
        find_concept_ids(data)
    # print(concept_ids)

    # unique concept-ids
    remove_duplicates(concept_ids)

    # remove concept IDs that don't start with C
    filtered_concept_ids = [concept_id for concept_id in concept_ids if concept_id.startswith('C')]

    print(filtered_concept_ids)

    # Working concept-id
    # concept_id = "C3442474619-LARC_CLOUD"

    DATE_RANGE = ("2023-01-01", "2023-01-02")

    # Get datasets for different concept IDs
    for concept_id in filtered_concept_ids:
        concept_id_data = earthaccess.search_datasets(
            keyword=satellite_key,
            concept_id = concept_id,
            cloud_hosted=True,
            temporal=DATE_RANGE,
        )

        granules = []
        for dataset in concept_id_data:
            dataset_granules = earthaccess.search_data(
                concept_id=dataset["meta"]["concept-id"],  # get the dataset's concept-id
                cloud_hosted=True,
                temporal=DATE_RANGE,
            )
            granules.extend(dataset_granules)

        
        for granule in granules:
            try:
                files = earthaccess.download(granule, local_path=HE5_DATA_FOLDER)  # specify your destination folder
                print(f"Downloaded: {files}")
            except:
                print("Failed to download")


SATALLITE_KEY = "MOPITT"
# fetch_dataset(SATALLITE_KEY)

## Convert he5 format to JSON for easily readable format
# DATASET_JSON_FOLDER = "./data2json"
# he5_to_json.he5_to_json("./data2/MOP03J-20221119-L3V5.10.3.he5", DATASET_JSON_FOLDER+"/MOP03J-20221119-L3V5.10.3.json")


def add_unique_elements(input_list):
    unique_list = []
    for item in input_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


def add_non_repeating_items(list_a, list_b):
    for item in list_a:
        if item not in list_b:
            list_b.append(item)
    return list_b

result_data = { "satellite_key": SATALLITE_KEY,
                "keys": [],
                "temperature": [],
                "pressure": [],
                "CO_mix_ratio": [] }

# Access keys are added for every satellite key
# TODO: Code needs updating incase of fetching data from different satellite keys
def explore_group(group, path=""):
    access_keys = []
    for key in group.keys():
        item = group[key]
        full_path = f"{path}/{key}" if path else key

        if isinstance(item, h5py.Group):
            # print(f"Group: {full_path}")
            explore_group(item, full_path)
        elif isinstance(item, h5py.Dataset):
            # print(f"Dataset: {full_path}")
            try:
                data = item[()]
                access_keys.append(full_path)
                # print(f"  Data shape: {data.shape}")
                # print(data.flat[:])
                # print(f"  Sample data: {data if data.size < 100 else data.flat[:100]}")
            except Exception as e:
                print(f"  Could not read data: {e}")

    
    result_data["keys"]= add_non_repeating_items(access_keys, result_data["keys"])

def handle_he5_data(file_name):
    with h5py.File(file_name, "r") as he5_file:
        # print("//////////////////////////////////////////")
        keys = explore_group(he5_file)
        
def list_files_and_extract_dates(folder_path):
    file_info = []

    # Regex pattern to extract date (8 digits after 'MOP02N-')
    date_pattern = re.compile(r'MOP02N-(\d{8})')

    for filename in os.listdir(folder_path):
        if filename.endswith('.he5'):
            match = date_pattern.search(filename)
            if match:
                date_str = match.group(1)
                file_info.append((filename, date_str))
    
    return file_info


def find_closest_index(array, key_value):
    array = np.array(array)
    index = (np.abs(array - key_value)).argmin()
    return index

def check_crop_conditions(input_crop, Tmin, Tmax, Pmin, Pmax, CO_min, CO_max, json_file='ideal_data.json'):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Find the crop
    for entry in data:
        if entry['crop'].lower() == input_crop.lower():
            Tideal = entry['Tideal']
            Pideal = entry['Pideal']
            CO_ideal = entry['CO_ideal']

            # Check all conditions
            if Tmin <= Tideal <= Tmax and Pmin <= Pideal <= Pmax and CO_min <= CO_ideal <= CO_max:
                return True  # 👍
            else:
                return False  # 👎

    # Crop not found
    return None

# Latitute and longitude values
INPUT_LAT = 20.23
INPUT_LON = 51.54

files_with_dates = list_files_and_extract_dates(HE5_DATA_FOLDER)
for fname, date in files_with_dates:
    # print(f"File: {fname}, Date: {date}")

    handle_he5_data(HE5_DATA_FOLDER + "/" + fname)

# print(result_data["keys"])

for fname, date in files_with_dates:
    # print(f"File: {fname}, Date: {date}")

    # "HDFEOS/SWATHS/MOP02/Geolocation Fields/Longitude"
    # "HDFEOS/SWATHS/MOP02/Geolocation Fields/Latitude"
    # "HDFEOS/SWATHS/MOP02/Data Fields/SurfacePressure"
    # "HDFEOS/SWATHS/MOP02/Data Fields/RetrievedCOSurfaceMixingRatio"
    # "HDFEOS/SWATHS/MOP02/Data Fields/APrioriSurfaceTemperature"

    with h5py.File(HE5_DATA_FOLDER + "/" + fname, "r") as he5_file:
        # Assumption: That the linear matrix is true in the X and Y directions

        lat_dataset = he5_file["HDFEOS/SWATHS/MOP02/Geolocation Fields/Latitude"]
        lon_dataset = he5_file["HDFEOS/SWATHS/MOP02/Geolocation Fields/Longitude"]
        surface_pressure_dataset = he5_file["HDFEOS/SWATHS/MOP02/Data Fields/SurfacePressure"]
        CO_ratio_dataset = he5_file["HDFEOS/SWATHS/MOP02/Data Fields/RetrievedCOSurfaceMixingRatio"]
        surface_temperature_dataset = he5_file["HDFEOS/SWATHS/MOP02/Data Fields/APrioriSurfaceTemperature"]
        # print(lat_dataset.shape)
        # print(surface_pressure_dataset.shape)
        # print(surface_temperature_dataset.shape)
        # print(CO_ratio_dataset.shape)

        lat_idx = find_closest_index(lat_dataset, INPUT_LAT)
        lon_idx = find_closest_index(lon_dataset, INPUT_LON)

        # Value for latittue & longitude intersection
        temperature = (surface_temperature_dataset[lat_idx][0] + surface_temperature_dataset[lon_idx][0]) / 2.0
        pressure = (surface_pressure_dataset[lat_idx] + surface_pressure_dataset[lon_idx]) / 2.0
        co_ratio = (CO_ratio_dataset[lat_idx][0] + CO_ratio_dataset[lon_idx][0]) / 2.0

        result_data["temperature"].append(temperature)
        result_data["CO_mix_ratio"].append(co_ratio)
        result_data["pressure"].append(pressure)
    

# print(f"temperature: {result_data['temperature']}")
# print(f"pressure: {result_data['pressure']}")
# print(f"CO_mixture: {result_data['CO_mix_ratio']}")

Tmax = max(result_data['temperature'])
Tmin = min(result_data['temperature'])
Pmax = max(result_data['pressure'])
Pmin = min(result_data['pressure'])
CO_ratio_max = max(result_data['CO_mix_ratio'])
CO_ratio_min = min(result_data['CO_mix_ratio'])

print(f"Tmax: {Tmax}, Tmin: {Tmin}")
print(f"Pmax: {Pmax}, Pmin: {Pmin}")
print(f"CO_ratio_max: {CO_ratio_max}, CO_ratio_min: {CO_ratio_min}")

result = check_crop_conditions(
    'mango',
    Tmin, Tmax,
    Pmin, Pmax,
    CO_ratio_min, CO_ratio_max
)

print("✅ Thumbs up!" if result else "❌ Conditions not met or crop not found.")

