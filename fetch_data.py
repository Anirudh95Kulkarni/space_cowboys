import earthaccess

# EARTHDATA_USERNAME="ultseid"
# EARTHDATA_PASSWORD="4d&vcVH9q@AT_FY"

earthaccess.login(strategy="environment")

results = earthaccess.search_datasets(
    keyword="icesat-2"
    )

print("#########################################################")
print("#########################################################")
print("#########################################################")
print("#########################################################")

print(len(results))

datasets = earthaccess.search_datasets(
    keyword="modis",
    bounding_box=(11°37'32.5"E, )
    cloud_hosted=True
)

print(len(datasets))



# Download dataset
# earthaccess.download()