import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    # PUT YOUR CODE HERE
    ref = pathlib.Path(ref)
    path = gitdir / ref
    f = path.open("w")
    f.write(new_value)
    f.close()


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    # PUT YOUR CODE HERE
    f = open(gitdir / name, "w")
    f.write(ref)
    f.close()


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    # PUT YOUR CODE HERE
    if refname == "HEAD":
        refname = get_ref(gitdir)
    detached = is_detached(gitdir)
    if detached:
        return refname
    with (gitdir / pathlib.Path(refname)).open("r") as f:
        data = f.read()
    return data


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    # PUT YOUR CODE HERE
    return ref_resolve(gitdir, "HEAD") if (gitdir / get_ref(gitdir)).exists() \
        else None


def is_detached(gitdir: pathlib.Path) -> bool:
    # PUT YOUR CODE HERE
    if not pathlib.Path.exists(gitdir / "HEAD"):
        return False
    f = open(gitdir / "HEAD", "r")
    data = f.read()
    f.close()
    if type(data) == str and len(data) == 40 and data[:5] != "ref: ":
        return True
    return False


def get_ref(gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    f = open(gitdir / "HEAD", "r")
    ref = f.read()
    f.close()
    if ref[:5] == "ref: ":
        ref = ref[5:-1]
    return ref
