import earthaccess
import h5py

# EARTHDATA_USERNAME="ultseid"
# EARTHDATA_PASSWORD="4d&vcVH9q@AT_FY"

earthaccess.login(strategy="environment")

# results = earthaccess.search_datasets(
#     keyword="icesat-2"
#     )

print("#########################################################")
print("#########################################################")
print("#########################################################")
print("#########################################################")

# print(len(results))

concept_id = "C3442474619-LARC_CLOUD"

datasets = earthaccess.search_datasets(
    keyword="MOPITT",
    concept_id = concept_id,
    # bounding_box=(11°37'32.5"E, 57°33'53.7"N, 12°34'54.2"E, 58°00'54.6"N),
    # boundig_box=(11.372166, 57.361942, 12.581345, 58.015171),
    cloud_hosted=True,
    count=1
)

date_range = ("2022-11-19", "2023-04-06")

## geo Coordinates

Xmin = 10.337235
Ymin = 54.977086
Xmax = 24.150210
Ymax = 69.743887
bbox = (Xmin, Ymin, Xmax, Ymax)

results = earthaccess.search_data(
    concept_id = concept_id,
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox,
)

print(type(results[0]))

# downloaded_files = earthaccess.download(
#     results[0:9],
#     local_path='./data',
# )


def explore_group(group, path=""):
    for key in group.keys():
        item = group[key]
        full_path = f"{path}/{key}" if path else key

        if isinstance(item, h5py.Group):
            print(f"Group: {full_path}")
            explore_group(item, full_path)
        elif isinstance(item, h5py.Dataset):
            print(f"Dataset: {full_path}")
            try:
                data = item[()]
                print(f"  Data shape: {data.shape}")
                print(f"  Sample data: {data if data.size < 10000 else data.flat[:10000]}")
            except Exception as e:
                print(f"  Could not read data: {e}")



for file in "./data":
    with h5py.File("data/MOP03J-20221119-L3V5.10.3.he5", "r") as he5_file:
        print("//////////////////////////////////////////")
        explore_group(he5_file)
        # print(list(he5_file.keys()))
        # print(list(he5_file["HDFEOS"]))
        # print(he5_file["HDFEOS"]["ADDITIONAL"])
        # print(he5_file['HDFEOS INFORMATION'])

# explore_group(he5_file)

# print(results)
# print((datasets[0]._basic_meta_fields_))
# print(datasets[0].get_data())
# print(datasets[0].services)
# print(datasets[0].services)


# print(len(datasets))



# Download dataset
# earthaccess.download()