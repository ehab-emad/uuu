"""
This Script ensures proper content classification of static
file's folder. Given a correct folder structure with main
.json file included, script lists all sub-folders and their
content and reflects it to main meta.json file. Usage is
as follows:
    run a command from a command prompt:
    .\meta_replication.py path_to_folder
Remarks: Given folder has to contain static files as well as
control file meta.json. Otherwise, script fails.
"""
from uuid import uuid4 as new_id
from uuid import UUID
import os
import json
import sys


def valid(in_uuid: str) -> bool:
    """
    Function checking validity of a given uuid in string form
    :param in_uuid: string uuid to check
    :return: bool if it is valid, otherwise false
    """
    try:
        UUID(in_uuid)
        return True
    except (TypeError, ValueError):
        return False


def walk(in_path: str) -> None:
    """
    Function walking through directories given and collecting
    all file paths that are in correspondence with desired
    file types. Moreover, UUIDs will be generated as well.
    :param in_path: string path of a folder to be checked
    :return: None
    """
    global output
    for subpath in os.listdir(in_path):
        output.append([str(new_id()), os.path.join(in_path, subpath).replace("\\", "/")]) \
            if ".png" in subpath or ".ico" in subpath or ".gif" in subpath else None
        walk(os.path.join(in_path, subpath)) if "." not in subpath else None
        pass
    pass


def main(in_path: str = None) -> None:
    """
    Main function that collects data and writes them into a meta.json file.
    Given system argument, path will be extracted from terminal command,
    otherwise, input string is used.
    :param in_path: string path of a folder to be checked
    :return: none
    """
    global output
    dir_path = in_path if in_path is not None else sys.argv[1]
    meta_path = os.path.join(dir_path, "meta.json")
    uuids, paths = list(), list()
    walk(dir_path)
    [(uuids.append(data[0]), paths.append(data[1])) for data in output]
    with open(meta_path, "r") as meta:
        try:
            current_meta = json.load(meta)
        except json.JSONDecodeError:
            current_meta = dict()
    for key, value in zip(current_meta.keys(), current_meta.values()):
        index = paths.index(value) if value in paths else None
        if index is not None:
            output[index][0] = key
        output.append([key, value]) if index is None and valid(key) and os.path.isfile(value) else None
        pass
    with open(meta_path, "w") as meta:
        meta.flush()
        meta.writelines("{\n")
        for line, count in zip(output, range(len(output))):
            koma = "" if count == len(output) - 1 else ","
            uuid, path = line[0], line[1].replace("\\", "/")
            meta.writelines(f'\t\"{uuid}\": \"{path}\"{koma}\n')
        meta.writelines("}")
        pass


if __name__ == "__main__":
    output = list()
    main()
    pass
