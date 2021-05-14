import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        # PUT YOUR CODE HERE
        name = str.encode(self.name)
        form = f"!10i20sh{len(name) + 3}s"
        return struct.pack(
            form,
            self.ctime_s, self.ctime_n, self.mtime_s, self.mtime_n,
            self.dev,
            self.ino,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            name
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        # PUT YOUR CODE HERE
        format = f"!10i20sh{len(data) - 62}s"
        unpacked = struct.unpack(format, data)
        unpacked = list(unpacked)
        unpacked[-1] = unpacked[-1].strip(b"\00")
        unpacked[-1] = unpacked[-1].decode()
        return GitIndexEntry(*unpacked)


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    # PUT YOUR CODE HERE
    reading_index, a, b, c = [], 62, 12, 0
    path = gitdir / 'index'
    if not path.exists():
        return reading_index
    else:
        with path.open("rb") as f:
            data = f.read()
    count = struct.unpack("!i", data[8:12])[0]
    data = data[12:]
    for step in range(count):
        b = data[a:].find(b"\x00\x00\x00")

        indexE = GitIndexEntry
        unpacked = indexE.unpack(data[c: a + b + 3])
        reading_index.append(unpacked)
        a += b + 65;
        c += b + 65
    return reading_index


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    # PUT YOUR CODE HERE
    path, data = gitdir / 'index', b"DIRC"
    data += struct.pack("!2i", 2, len(entries))
    for i in range(len(entries)):
        data += entries[i].pack()
    sha = hashlib.sha1(data).digest()
    data += sha

    with path.open("wb") as f:
        f.write(data)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    # PUT YOUR CODE HERE
    index = read_index(gitdir)
    for i in range(len(index)):
        name, mode, sha = index[i].name, index[i].mode, index[i].sha1.hex()
        if details:
            print(f"{mode:o} {sha} 0\t{name}")
        else:
            print(name)


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    # PUT YOUR CODE HERE
    index = []
    for i in paths:
        with i.open("rb") as f:
            data = f.read()
        entry = GitIndexEntry(
                ctime_s=int(os.stat(i).st_ctime),
                ctime_n=0,
                mtime_s=int(os.stat(i).st_mtime),
                mtime_n=0,
                dev=os.stat(i).st_dev,
                ino=os.stat(i).st_ino,
                mode=os.stat(i).st_mode,
                uid=os.stat(i).st_uid,
                gid=os.stat(i).st_gid,
                size=os.stat(i).st_size,
                sha1=bytes.fromhex(hash_object(data, "blob", write=True)),
                flags=len(i.name),
                name=str(i),
            )
        index.append(entry)
    if write:
        index_s = sorted(index, key=lambda x: x.name)
        write_index(gitdir, index_s)