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
        values = (
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode()
        )
        name = str(len(self.name.encode())) + "s"
        nul = "3x"
        s = struct.pack(f">10i20sh" + name + nul, *values)
        return s

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
    index = gitdir / "index"
    if not index.exists():
        return []
    with index.open("rb") as file:
        data = file.read()
    result = []
    header = data[:12]
    main_content = data[12:]
    main_content_copy = main_content
    for _ in range(struct.unpack(">I", header[8:])[0]):
        end_of_entry = len(main_content_copy) - 1
        for j in range(63, len(main_content_copy), 8):
            if main_content_copy[j] == 0:
                end_of_entry = j
                break
        result += [GitIndexEntry.unpack(main_content_copy[: end_of_entry + 1])]
        if len(main_content_copy) > end_of_entry:
            main_content_copy = main_content_copy[end_of_entry + 1:]
    return result


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    # PUT YOUR CODE HERE
    index_path = gitdir / "index"
    f = index_path.open(mode="wb")
    values = (b"DIRC", 2, len(entries))
    info = struct.pack(">4s2i", *values)
    to_hash = info
    f.write(info)
    for el in entries:
        f.write(el.pack())
        to_hash += el.pack()
    hash = hashlib.sha1(to_hash).hexdigest()
    f.write(struct.pack(f">{len(bytearray.fromhex(hash))}s", bytearray.fromhex(hash)))
    f.close()


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    # PUT YOUR CODE HERE
    for entry in read_index(gitdir):
        if details:
            print(f"{entry.mode:o} {entry.sha1.hex()} 0\t{entry.name}")
        else:
            print(entry.name)


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
    if write:
        write_index(gitdir, sorted(entries, key=lambda x: x.name))
