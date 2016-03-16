#!/usr/local/bin/python3
from plistlib import load, InvalidFileException
from os.path import basename, realpath, join, isdir, islink
from os import walk, symlink, chdir, unlink
from sys import argv, stdin
from re import match

version_dir = "/Library/Frameworks/R.framework/Versions/"
usage = "Usage: rswitch [version]\n"

if not isdir(version_dir):
    print("\n%s is not a directory.\n")
    exit(1)

r_versions = [{"v": x} for x in next(walk(version_dir))[1] if x != "Current"]

if len(r_versions) == 0:
    print("\nNo R versions found in %s\n" % version_dir)
    exit(0)

if islink(join(version_dir, "Current")):
    current = basename(realpath(join(version_dir, "Current")))
else:
    current = None
    print("\nNB: No Current version in use.")

for r in r_versions:
    if r["v"] == current:
        r["current"] = True
    else:
        r["current"] = False
    try:
        fn = open(join(version_dir, r["v"], "Resources", "Info.plist"), 'rb')
        pl = load(fn)
        r["long"] = pl["CFBundleVersion"]
    except (FileNotFoundError, InvalidFileException):
        r["long"] = None

if len(argv) > 2:
    print("\nERROR: More than 1 arguments supplied.")
    print("")
    print(usage)
    exit(1)

def print_version(i, r):
    cols = []
    v = r["v"]
    if r["current"]:
        v = "=> " + v
    v = v.rjust(8)
    cols.append("    [" + str(i) + "]")
    cols.append(v)
    if r["long"] is not None:
        cols.append("   " + r["long"])
    else:
        cols.append("   " + "[incomplete installation]")
    print(" ".join(cols))

def print_all(r_v):
    for i, r in enumerate(r_versions):
        print_version(i+1, r_versions[i])
    print("")

if len(argv) == 1:
    print("\nAvalable versions:\n")
    print_all(r_versions)
    print(usage)

is_int = lambda x: match(r"^\d+$", x) is not None
is_short = lambda x: match(r"^\d\.\d$", x) is not None
is_long = lambda x: match(r"^\d\.\d\.\d$", x) is not None

if len(argv) == 2:
    v = argv[1]
    if is_short(v):
        if v in [r["v"] for r in r_versions]:
            path = v
        elif int(v[0]) > 3:
            print("\nThis is a python script not a time machine\n")
            exit(42)
        else:
            print("\nVersion %s is not installed. Available versions are:\n" % v)
            print_all(r_versions)
            exit(0)
    elif is_long(v):
        if v in [r["long"] for r in r_versions]:
            path = v[0:3]
        elif v[0:3] in [r["v"] for r in r_versions]:
            available = [r["long"] for r in r_versions if r["v"] == v[0:3]]
            msg = "\nVersion %s is not installed, however R %s is still available as version %s.\n"
            print(msg % (v, v[0:3], available[0]))
            print("Switch to version %s? [Y/n]" % available[0])
            answer = stdin.read(1)
            if answer in ["Y", "y", "\n"]:
                path = v[0:3]
            else:
                exit(0)
        else:
            print("\nVersion %s is not installed. Available versions are:" % v)
            print_all(r_versions)
            exit(0)
    elif is_int(v):
        if v in map(str, range(1, len(r_versions)+1)):
            path = r_versions[int(v)-1]["v"]
        else:
            print("\nThere are not that many versions of R installed. Available versions are:\n")
            print_all(r_versions)
            exit(0)
    elif v.lower() == "devel":
        path = r_versions[-1]["v"]
    else:
        print("\nERROR: Argument not understood\n")
        print(usage)
        exit(1)

    if path == current:
        print("\nVersion %s already in use.\n" % path)
    else:
        chdir(version_dir)
        if current is not None:
            unlink("Current")
        symlink(path, "Current")
        print("\nSwitched to version %s\n" % path)

    if [r["long"] for r in r_versions if r["v"] == path][0] is None:
        print("WARNING: Current R version does not appear to be correctly installed\n")

    exit(0)

