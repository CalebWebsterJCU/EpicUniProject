"""
EPIC UNI PROJECT
2021
Program written for North Queensland Engineering to assist them in the
analysis of stresses on weld beads in a high-pressure vessel.
"""

import json


def main():
    """Read, write, and edit all required files."""
    # Read weld data.
    weldbodies = read_csv_data("weld_data.csv", convert_ints=True)
    # Write json files.
    for weldbody in weldbodies:
        write_weldbody_file(weldbody)
    # Edit json files.
    edit_parameter_file("ProjectParameters.json", weldbodies, copy=False)
    edit_parameter_file("Welding_ProjectParameters.json", weldbodies, copy=False)
    edit_recipe_file("Welding_recipe.json", weldbodies, copy=False)


def read_csv_data(filename, convert_ints=False):
    """
    Read and return information about weld beads from a csv file.
    
    :param str filename: name of csv file to read.
    :param boolean convert_ints: if True, convert certain fields to integers.
    :return: list of dictionaries containing weld bead info.
    """
    weldbodies = []
    with open(filename, 'r') as file_in:
        file_in.readline()  # Skip first line (labels)
        line = file_in.readline()
        while line and line[0] != ',':  # Repeat until blank line is found (blank line starts with ',').
            line = line.split(',')
            # print(line)
            try:
                data = {
                    "name": line[0],
                    "json_file_name": line[0] + ".json",
                    "weld_body": int(line[1]),
                    "start_node_id": int(line[2]),
                    "middle_node_id": int(line[3]),
                    "end_node_id": int(line[4]),
                    "midpoint_x": float(line[5]),
                    "midpoint_y": float(line[6]),
                    "midpoint_z": float(line[7]),
                    "norm_vector_x": float(line[8]),
                    "norm_vector_y": float(line[9]),
                    "norm_vector_z": float(line[10]),
                    "heat_source_depth": float(line[11]),
                    "heat_source_front_length": float(line[12]),
                    "heat_source_power": int(line[13]),
                    "heat_source_rear_length": float(line[14]),
                    "heat_source_speed": float(line[15]),
                    "heat_source_width": float(line[16]),
                    "start_time": int(line[17])
                }
            except ValueError:
                print("One or more data types were incorrect.")
            if convert_ints:
                data["norm_vector_x"] = int(data["norm_vector_x"])
                data["norm_vector_y"] = int(data["norm_vector_y"])
            # print(data)
            weldbodies.append(data)
            line = file_in.readline()
    return weldbodies


def write_weldbody_file(wb):
    """
    Create a json file and store all weldbody data inside.
    
    :param dict wb: dictionary storing all weldbody information.
    """
    # Create json data in the correct format.
    json_data = {
        "weld_path_node_list": [
            {"Nodeid": wb["start_node_id"], "WeldSurfaceMidPoint": [wb["midpoint_x"], wb["midpoint_y"], wb["midpoint_z"]], "WeldSurfaceNormalVector": [wb["norm_vector_x"], wb["norm_vector_y"], wb["norm_vector_z"]]},
            {"Nodeid": wb["middle_node_id"], "WeldSurfaceMidPoint": [wb["midpoint_x"], wb["midpoint_y"], wb["midpoint_z"]], "WeldSurfaceNormalVector": [wb["norm_vector_x"], wb["norm_vector_y"], wb["norm_vector_z"]]},
            {"Nodeid": wb["end_node_id"], "WeldSurfaceMidPoint": [wb["midpoint_x"], wb["midpoint_y"], wb["midpoint_z"]], "WeldSurfaceNormalVector": [wb["norm_vector_x"], wb["norm_vector_y"], wb["norm_vector_z"]]}
        ]
    }
    # Write json data to file.
    with open(wb["json_file_name"], 'w') as file_out:
        print(json.dumps(json_data), file=file_out)


def edit_parameter_file(filename, weldbodies, copy=True):
    """
    Edit json parameter file to contain the actual weldbody filenames.
    
    By default, both parameter files contain ".json" instead of the
    actual filename. The files to be edited are:
    "Welding_ProjectParameters.json"
    "ProjectParameters.json"
    
    :param str filename: name of recipe file to edit.
    :param list weldbodies: list of weldbodies' information to insert.
    :param boolean copy: if True, create a copy of file with new name.
    """
    # Read contents from file.
    with open(filename, 'r') as file_in:
        contents = json.loads(file_in.read())
    # Update parameters for all weldbodies.
    custom_processes = contents["analysis_stages"][0]["processes"]["custom_processes"]
    for x in range(len(custom_processes)):
        wb = weldbodies[x]
        params = custom_processes[x]["Parameters"]
        params["heat_source_depth"] = wb["heat_source_depth"]
        params["heat_source_front_length"] = wb["heat_source_front_length"]
        params["heat_source_power"] = wb["heat_source_power"]
        params["heat_source_rear_length"] = wb["heat_source_rear_length"]
        params["heat_source_speed"] = wb["heat_source_speed"]
        params["heat_source_width"] = wb["heat_source_width"]
        params["include_json"] = wb["json_file_name"]
        params["start_time"] = wb["start_time"]
    # Write contents back into file.
    with open(filename[:-5] + "_Edited" + ".json" if copy else filename, 'w') as file_out:
        print(json.dumps(contents), file=file_out)


def edit_recipe_file(filename, weldbodies, copy=True):
    """
    Edit json recipe file contain the actual weldbody filenames.
    
    By default, the recipe file contains ".json" instead of the actual
    filename. The file to be edited is:
    "Welding_recipe.json"
    
    :param str filename: name of recipe file to edit.
    :param list weldbodies: list of weldbodies' information to insert.
    :param boolean copy: if True, create a copy of file with new name.
    """
    # Read contents from file.
    with open(filename, 'r') as file_in:
        contents = json.loads(file_in.read())
    # Choose the first weldbody to update heat source parameters.
    wb = weldbodies[0]
    hs_params = contents["heat_source_list"]["HeatSource_5"]
    hs_params["power"] = wb["heat_source_power"]
    hs_params["front_length"] = wb["heat_source_front_length"]
    hs_params["rear_length"] = wb["heat_source_rear_length"]
    hs_params["width"] = wb["heat_source_width"]
    hs_params["depth"] = wb["heat_source_depth"]
    # Update parameters for all weldbodies.
    for k in contents["weld_sequence_list"]:
        robot = contents["weld_sequence_list"][k]
        for x in range(len(robot)):
            wb = weldbodies[x]
            params = robot[x]
            params["trajectory"] = wb["json_file_name"]
            params["speed"] = wb["heat_source_speed"]
            params["start_time"] = wb["start_time"]
    # Write contents back into file.
    with open(filename[:-5] + "_Edited" + ".json" if copy else filename, 'w') as file_out:
        print(json.dumps(contents), file=file_out)


if __name__ == '__main__':
    main()
