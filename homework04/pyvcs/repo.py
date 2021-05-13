import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    # PUT YOUR CODE HERE
    gitdir_name = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    while pathlib.Path(workdir.absolute().root) != workdir.absolute():
        if (workdir / gitdir_name).is_dir():
            return workdir / gitdir_name
        workdir = workdir.parent
    if (workdir / gitdir_name).is_dir():
        return workdir / gitdir_name
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    # PUT YOUR CODE HERE
    gitdir_name = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    if workdir.is_file():
        raise Exception(f"{workdir} is not a directory")
    os.makedirs(workdir / gitdir_name / "refs" / "heads", exist_ok=True)
    os.makedirs(workdir / gitdir_name / "refs" / "tags", exist_ok=True)
    (workdir / gitdir_name / "objects").mkdir()
    with (workdir / gitdir_name / "config").open("w") as f:
        f.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n",
        )
    with (workdir / gitdir_name / "HEAD").open("w") as f:
        f.write("ref: refs/heads/master\n")
    with (workdir / gitdir_name / "description").open("w") as f:
        f.write("Unnamed pyvcs repository.\n")
    return workdir / gitdir_name
