import os
from pathlib import Path
import pytest
from utils import set_new_version

import pytest

path = "path_to_file.txt"
path1 = "path_to_file_v01.txt"
path11 = "path_to_file_v11.txt"
path_no_extension = "path_to_file"
path_no_name = ".txt"

with open(path, "w") as f:
    f.write(" ")

with open(path1, "w") as f:
    f.write(" ")

with open(path11, "w") as f:
    f.write(" ")

with open(path_no_extension, "w") as f:
    f.write(" ")


with open(path_no_name, "w") as f:
    f.write(" ")


class TestSetNewVersion:

    # Returns a Path object with the updated file path with a new version.
    def test_returns_updated_file_path(self):

        in_path = Path(path)
        expected_path = "path_to_file_v01.txt"
        result = set_new_version(in_path)

        assert result.name == expected_path

        in_path = Path(path11)
        expected_path = "path_to_file_v12.txt"
        result = set_new_version(in_path)

        assert result.name == expected_path

    # Adds a versioning suffix to the file name.
    def test_adds_versioning_suffix(self):
        expected_path = "path_to_file.v01.txt"
        result = set_new_version(path, versioning_suffix=".v")

        assert result.name == expected_path


        in_path = Path(path11, versioning_suffix=".v")
        # ! version is already created as _v11 and should not be changed.
        expected_path = "path_to_file_v12.txt"
        result = set_new_version(in_path)

        assert result.name == "path_to_file_v12.txt"

    # Increments the version number by 1.
    def test_overwrite(self):
        in_path = str(path11)
        expected_path = "path_to_file_v11.txt"

        result = set_new_version(in_path, overwrite=True)

        assert in_path == expected_path

    # Handles file paths with no parent folder.
    def test_path_exists(self):
        in_path = Path("file.txt")

        with pytest.raises(FileExistsError):
            set_new_version(in_path)


    # Handles file paths with no extension.
    def test_handles_no_extension(self):
        in_path = Path("path_to_file")
        expected_path = "path_to_file_v01"

        result = set_new_version(in_path)

        assert result.name == expected_path

    # Handles file paths with no name.
    def test_handles_no_name(self):
        in_path = path_no_name
        expected_path = "_v01.txt"

        result = set_new_version(in_path)

        os.remove(path)
        os.remove(path1)
        os.remove(path11)
        os.remove(path_no_name)

        assert result.name == expected_path