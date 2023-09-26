import os
from pathlib import Path
import time
import inspect
from functools import wraps
from typing import Iterable

import yaml
from rich import print
from rich.align import Align


_SEP_ = "__"


def flatten_list(lst: list) -> list:
    """Recursive flattening of lists.
    exi
        Args:
            lst (list):

        Returns:
            flattened list (list)
    """
    return [
        item
        for sublist in lst
        for item in (
            flatten_list(sublist) if isinstance(sublist, list) else [sublist]
        )
    ]


def replace_backslash(d: dict):
    """
    Recursively replaces all occurrences of the string "\\t" with a
    tab character ("\t") and all occurrences of the string "\\n"
    with a newline character ("\n") in a nested dictionary.

    Function necessary to fix values from config.yaml and apply
    delimiters when writing .fem.

    Args:
        d (dict): A dictionary to replace.

    Returns:
        dict: The modified nested dictionary.
    """

    for k, v in d.items():
        if isinstance(v, dict):
            replace_backslash(v)
        elif isinstance(v, str) and "t" in v:
            newv = v.replace("\\t", "\t")
            if isinstance(v, str) and "n" in v:
                newv = newv.replace("\\n", "\n")
            d[k] = newv
    return d


def tagm_load_config(file_name: str = "config.yaml") -> dict:
    """Load config.yaml.
    File should be in the root directory of the project.


    Args:
        file_name (str, optional): Defaults to 'config.yaml'.

    Returns:
        config dict

    """
    root_dir = Path(__file__).parents[1]
    path = root_dir.joinpath(file_name)
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    return config


def ffw_params(file_name: str = "config.yaml") -> dict:
    """Load config.yaml.
    File should be in the root directory of the project.


    Args:
        file_name (str, optional): Defaults to 'config.yaml'.

    Returns:
        tuple: ffw params
            _ENCODING_,
            _KEYWORDS_,
            _STRICT_ORDER_,
            _DELIMITER_,
            _OFFSET_FILE_

    """
    config = tagm_load_config()

    return (
        config["_ENCODING_"],
        list(config["_KEYWORDS_"].keys()),
        config["_STRICT_ORDER_"],
        replace_backslash(config["_KEYWORDS_"]),
        config["offset"],
    )


def change_file_name(in_path: Path, change: str, suffix: bool = True) -> Path:
    """add suffix or prefix to Path.

    Args:
        in_path (Path): input
        change (str): suffix or prefix to be added.
        suffix (bool, optional): if True, suffix, else prefix.
            Defaults to True.

    Returns:
        Path: path with new file name.
    """

    folder = in_path.parents[0]
    extension = in_path.suffix
    name = in_path.name.split(extension)[0]
    if suffix:
        out_name = f"{name}{change}{extension}"
    else:
        out_name = f"{change}{name}{extension}"
    return folder.joinpath(out_name)


def get_last_version(in_path: Path) -> Path:
    """Get last version of other files in folder, given input path.
    Valid for naming scheme with numbering.

    Args:
        in_path (Path): input

    Returns:
        Path: path of last version
    """
    in_path = Path(in_path)
    folder = in_path.parents[0]
    extension = in_path.suffix
    name = in_path.name.split(extension)[0]
    files = [
        file
        for file in os.listdir(folder)
        if name == file.split("_v")[0]
        if "$" not in file
    ]
    if not files:
        return folder.joinpath(name + extension)

    last_v = sorted(files)[-1].split(".")[0] + extension

    return folder.joinpath(last_v)


def set_new_version(
    in_path: Path, versioning_suffix="_v", overwrite: bool = False
) -> Path:
    """Add sufix to file in case it already exists in the directory.

    Args:
        in_path (Path): input

    Returns:
        Path: path to the new last version
    """

    if overwrite:
        return in_path

    folder = in_path.parents[0]
    extension = in_path.suffix
    name_w_version = in_path.name.split(extension)[0]

    splitted_name = name_w_version.split("_v")
    if len(splitted_name) == 1:
        version = "00"
    else:
        version = splitted_name[1]

    name = name_w_version.split("_v")[0]
    new_version = int(version) + 1
    if new_version < 10:
        new_version = f"0{new_version}"
    else:
        new_version = str(new_version)

    return folder.joinpath(
        f"{name}{versioning_suffix}{new_version}{extension}"
    )


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        start = "\n\n\n\n\n****************************"
        m1 = f" [bold green]{func.__name__}[/bold green] took "
        m2 = f"[bold blue]{elapsed_time:.2f}[/bold blue] seconds to run. "
        end = "****************************"
        msg = f"{start}{m1}{m2}{end}"
        if kwargs.get("verbose"):
            info = Align.center(msg)
            print(info)
        return result

    return wrapper


def change_extension(in_path: Path, new_extension: str) -> Path:
    """Update file path extension

    Args:
        in_path (Path): input path
        new_extensiom (str)

    Returns:
        Path: path of last version
    """
    folder = in_path.parents[0]
    extension = in_path.suffix
    name = in_path.name.split(extension)[0]
    return folder.joinpath(name + new_extension)


def check_arguments(func, *args, **kwargs):
    """Check if the arguments are valid for the given function.

    Args:
        func (function): The function to check the arguments for.
        *args: The positional arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Raises:
        TypeError: If the arguments are not valid for the function.
    """
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    for name, value in bound.arguments.items():
        param = sig.parameters[name]
        if not isinstance(value, param.annotation):
            raise TypeError(
                f"Invalid argument type for {name}: "
                f"expected {param.annotation}, "
                f"got {type(value)}"
            )


def flatten_dict(d: dict, parent_key="", sep: str = _SEP_):
    """Function to flatten the config file.
    It is used as a helper to smooth the
    checking of variable types in the config.yaml file.

    Args:
        d (dict): config dict to be flattened.
        parent_key (str, optional)
        sep (str, optional): Defaults to _SEP_.

    Returns:
        dict: flattened dictionary
    """

    items = []
    for k, v in d.items():
        new_key = str(parent_key) + sep + str(k) if parent_key else str(k)
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def is_iterable(obj: Iterable) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False
