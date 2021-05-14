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
    obj = zlib.compress(store)
    if write:
        gitdir = repo_find()
        obj_dir = pathlib.Path(str(gitdir) + "/objects/" + res[:2])
        if not obj_dir.is_dir():
            os.makedirs(obj_dir)
        obj_name = obj_dir / res[2:]
        with open(obj_name, "wb") as obj_file:
            obj_file.write(obj)
    return res


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    # PUT YOUR CODE HERE
    if 4 > len(obj_name) or len(obj_name) > 40:
        raise Exception(f"Not a valid object name {obj_name}")
    objects = repo_find() / "objects"
    obj_list = []
    for file in (objects / obj_name[:2]).glob("*"):
        cur_obj_name = file.parent.name + file.name
        if obj_name == cur_obj_name[: len(obj_name)]:
            obj_list.append(cur_obj_name)
    if not obj_list:
        raise Exception(f"Not a valid object name {obj_name}")
    return obj_list


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    return resolve_object(obj_name, gitdir)[0]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    # PUT YOUR CODE HERE
    with (gitdir / "objects" / sha[:2] / sha[2:]).open("rb") as f:
        data = zlib.decompress(f.read())
    return data.split(b" ")[0].decode(), data.split(b"\00", maxsplit=1)[1]


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    # PUT YOUR CODE HERE
    tree = []
    while data:
        start_sha = data.index(b"\00")
        mode_b, name_b = map(lambda x: x.decode(), data[:start_sha].split(b" "))
        sha = data[start_sha + 1: start_sha + 21]
        tree.append((int(mode), name, sha.hex()))
        data = data[start_sha + 21:]
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


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    fmt, content = read_object(tree_sha, gitdir)
    objects = read_tree(content)
    ar = []
    for i in objects:
        if i[0] == 100644:
            ar.append((i[1], i[2]))
        else:
            sub_objects = find_tree_files(i[2], gitdir)
            for j in sub_objects:
                ar.append((i[1] + "/" + j[0], j[1]))
    return ar


def commit_parse(raw: bytes, start: int = 0, dct=None):
    # PUT YOUR CODE HERE
    res: tp.Dict[str, tp.Any] = {"message": []}
    for i in map(lambda x: x.decode(), raw.split(b"\n")):
        if "tree" in i or "parent" in i or "author" in i or "committer" in i:
            name, val = i.split(" ", maxsplit=1)
            res[name] = val
        else:
            res["message"].append(i)
    return res
