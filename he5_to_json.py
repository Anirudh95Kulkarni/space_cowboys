import h5py
import json
import numpy as np

def safe_serialize(value):
    """Convert non-JSON-serializable types (like bytes) to strings."""
    if isinstance(value, (bytes, np.bytes_)):
        try:
            return value.decode('utf-8', errors='ignore')
        except Exception:
            return value.hex()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.integer, np.floating)):
        return value.item()
    else:
        return value


def read_hdf5_group(group):
    """Recursively read an HDF5 group and return it as a Python dict."""
    data_dict = {}

    for key, item in group.items():
        if isinstance(item, h5py.Dataset):
            try:
                data = item[()]
                if isinstance(data, np.ndarray) and data.ndim == 0:
                    data = data.item()
                data_dict[key] = safe_serialize(data)
            except Exception as e:
                data_dict[key] = f"Could not read dataset ({e})"
        elif isinstance(item, h5py.Group):
            data_dict[key] = read_hdf5_group(item)

    # Include attributes if available
    attrs = {}
    for attr_name, attr_value in group.attrs.items():
        attrs[attr_name] = safe_serialize(attr_value)
    if attrs:
        data_dict["_attributes"] = attrs

    return data_dict


def he5_to_json(he5_path, json_path):
    """Convert a .he5 file to JSON."""
    with h5py.File(he5_path, 'r') as file:
        data = read_hdf5_group(file)
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Conversion complete! JSON saved to: {json_path}")


# Example usage:
# input_file = "data/MOP03J-20221119-L3V5.10.3.he5"
# output_file = "out_data/MOP03J-20221119-L3V5.10.3.json"

# he5_to_json(input_file, output_file)
