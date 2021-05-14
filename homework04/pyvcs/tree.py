import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    # PUT YOUR CODE HERE
    tree_entries = []
    for entry in index:
        _, name = os.path.split(entry.name)
        if dirname:
            names = dirname.split("/")
        else:
            names = entry.name.split("/")
        if len(names) != 1:
            prefix = names[0]
            name = f"/".join(names[1:])
            mode = "40000"
            tree_entry = f"{mode} {prefix}\0".encode()
            tree_entry += bytes.fromhex(write_tree(gitdir, index, name))
            tree_entries.append(tree_entry)
        else:
            if dirname and entry.name.find(dirname) == -1:
                continue
            with open(entry.name, "rb") as content:
                data = content.read()
            mode = str(oct(entry.mode))[2:]
            tree_entry = f"{mode} {name}\0".encode()
            tree_entry += bytes.fromhex(hash_object(data, "blob", write=True))
            tree_entries.append(tree_entry)

    tree_binary = b"".join(tree_entries)
    return hash_object(tree_binary, "tree", write=True)


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    # PUT YOUR CODE HERE
    if author is None and "GIT_AUTHOR_NAME" in os.environ and "GIT_AUTHOR_EMAIL" in os.environ:
        author = (
                os.getenv("GIT_AUTHOR_NAME", None)
                + " "
                + f'<{os.getenv("GIT_AUTHOR_EMAIL", None)}>'
        )
    if time.timezone > 0:
        timezone = "-"
    else:
        timezone = "+"
    timezone += f"{abs(time.timezone) // 60 // 60:02}{abs(time.timezone) // 60 % 60:02}"
    data = [f"tree {tree}"]
    if parent is not None:
        data.append(f"parent {parent}")
    data.append(f"author {author} {int(time.mktime(time.localtime()))} {timezone}")
    data.append(f"committer {author} {int(time.mktime(time.localtime()))} {timezone}")
    data.append(f"\n{message}\n")
    return hash_object("\n".join(data).encode(), "commit", write=True)
