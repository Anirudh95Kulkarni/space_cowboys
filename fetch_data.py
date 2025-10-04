import earthaccess
import h5py
import he5_to_json

# Use these as environment variables with your own login credentials
# EARTHDATA_USERNAME="Add_your_USERNAME_in_your_environment"
# EARTHDATA_PASSWORD="Add_your_PASSWORD_in_your_environment"
earthaccess.login(strategy="environment")

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
                files = earthaccess.download(granule, local_path="./data2")  # specify your destination folder
                print(f"Downloaded: {files}")
            except:
                print("Failed to download")


SATALLITE_KEY = "MOPITT"
fetch_dataset(SATALLITE_KEY)

## Convert he5 format to JSON for easily readable format
# DATASET_JSON_FOLDER = "./data2json"
# he5_to_json.he5_to_json("./data2/MOP03J-20221119-L3V5.10.3.he5", DATASET_JSON_FOLDER+"/MOP03J-20221119-L3V5.10.3.json")

# def explore_group(group, path=""):
#     for key in group.keys():
#         item = group[key]
#         full_path = f"{path}/{key}" if path else key

#         if isinstance(item, h5py.Group):
#             print(f"Group: {full_path}")
#             explore_group(item, full_path)
#         elif isinstance(item, h5py.Dataset):
#             print(f"Dataset: {full_path}")
#             try:
#                 data = item[()]
#                 # print(f"  Data shape: {data.shape}")
#                 # print(f"  Sample data: {data if data.size < 1000 else data.flat[:1000]}")
#             except Exception as e:
#                 print(f"  Could not read data: {e}")



# for file in "./data2":
#     with h5py.File("data/MOP03J-20221119-L3V5.10.3.he5", "r") as he5_file:
#         print("//////////////////////////////////////////")
#         explore_group(he5_file)
        
#         # Stop after 1 file
#         break
#         # print(list(he5_file.keys()))
#         # print(list(he5_file["HDFEOS"]))
#         # print(he5_file["HDFEOS"]["ADDITIONAL"])
#         # print(he5_file['HDFEOS INFORMATION'])

# explore_group(he5_file)
