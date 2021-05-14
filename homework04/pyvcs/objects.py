import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    # PUT YOUR CODE HERE
    header = f"{fmt} {len(data)}\0".encode()
    store = header + data
    res = hashlib.sha1(store).hexdigest()
    if write:
        path = repo_find() / "objects" / res[:2]
        path.mkdir(exist_ok=True)
        with (path / res[2:]).open("wb") as f:
            new_data = (fmt + " " + str(len(data))).encode()
            new_data = new_data + b"\00" + data
            f.write(zlib.compress(new_data))
    return res


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    # PUT YOUR CODE HERE
    path = gitdir / "objects"
    if 4 > len(obj_name) > 40:
        raise AssertionError(f"Not a valid object name {obj_name}")
    a = []
    for i in (path / obj_name[:2]).glob(f"{obj_name[2:]}*"):
        a.append(obj_name[:2] + i.name)

    if not a:
        raise AssertionError(f"Not a valid object name {obj_name}")
    return a


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    return str(gitdir) + "/" + obj_name[:2] + "/" + obj_name[2:]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    # PUT YOUR CODE HERE
    obj_name = resolve_object(sha, gitdir)[0]
    path = gitdir / "objects" / pathlib.Path(obj_name[:2]) / pathlib.Path(obj_name[2:])
    with path.open("rb") as f:
        file = f.read()
        data = zlib.decompress(file)

    border = data.find(b"\x00")
    header, content = data[:border], data[border + 1 :]

    border = header.find(b" ")
    fmt = header[:border].decode("ascii")

    return fmt, content


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    # PUT YOUR CODE HERE
    tree = []
    while len(data) > 0:
        border = -21
        sha = bytes.hex(data[border+1:])
        data = data[:border]

        gitdir = repo_find()
        fmt, content = read_object(sha, gitdir)

        border = data.rfind(b" ")
        name = data[border+1:].decode("ascii")
        data = data[:border]

        border = -6
        mode = "40000" if fmt == "tree" else data[border:].decode("ascii")
        border = len(mode)
        mode = int(mode)
        data = data[:-border]

        tuple = mode, sha, name
        tree.insert(0, tuple)
    return tree


def cat_file(obj_name: str, pretty: bool = True) -> None:
    # PUT YOUR CODE HERE
    gitdir = repo_find()
    fmt, content = read_object(obj_name, gitdir)
    if fmt == "blob":
        print(content.decode("ascii") if pretty else str(content))
    elif fmt == "tree":
        tree = read_tree(content)
        for i in tree:
            mode = i[0]
            mode = str(mode)
            lenght, value = len(mode), 6
            if lenght != value:
                mode = "0" + mode
            print(f"{mode} {read_object(i[1], gitdir)[0]} {i[1]}\t{i[2]}")
    else:
        obj_name1 = resolve_object(obj_name, gitdir)[0]
        print(read_object(obj_name1, gitdir)[1].decode())


def find_tree_files(tree_sha: str, gitdir: pathlib.Path, count: str = "") -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    files = []
    for i in read_tree(read_object(tree_sha, gitdir)[1]):
        tree_sha1 = i[1]
        fmt, content = read_object(tree_sha1, gitdir)
        parent = gitdir.parent
        path = pathlib.Path(i[2])
        path = path.relative_to(parent)

        appended = str(path)
        if path.is_dir():
            count += appended
            count += "/"
        if fmt == "tree":
            files += find_tree_files(tree_sha1, gitdir, count)
        else:
            tuple = (tree_sha1, count + appended)
            files.append(tuple)
    return files


def commit_parse(raw: bytes, start: int = 0, dct=None):
    # PUT YOUR CODE HERE
    border = 5
    data = raw.decode("ascii")[border:]
    border = data.find("author")
    return data[:border-2]
