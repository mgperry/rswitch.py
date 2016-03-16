#!/usr/local/bin/python3
from plistlib import load
from os.path import basename, realpath, join, isdir
from os import walk, symlink, chdir, unlink
from sys import argv

version_dir = "/Library/Frameworks/R.framework/Versions/"
usage = "\nUsage: rswitch [version]\n"

if not isdir(version_dir):
    print("\n%s is not a directory.\n")
    exit(1)

r_versions = next(walk(version_dir))[1]

if len(r_versions) == 0:
    print("\nNo R versions found in %s\n" % version_dir)
    exit(0)

try:
    r_versions.remove("Current")
    current = basename(realpath(join(version_dir, "Current")))
except ValueError:
    current = None
    print("\nNB: No Current version in use.")

long_version = []

for r in r_versions:
    try:
        fn = open(join(version_dir, r, "Resources", "Info.plist"), 'rb')
        pl = load(fn)
        long_version.append(pl["CFBundleVersion"])
    except:
        long_version.append(None)

if len(argv) > 2:
    print("\nERROR: More than 1 arguments supplied.")
    print(usage)
    exit(1)

if len(argv) == 1:
    print("")
    for i, r in enumerate(r_versions):
        cols = []
        v = r
        if r == current:
            v = "=> " + v
        v = v.rjust(8)
        cols.append("[" + str(i+1) + "]")
        cols.append(v)
        if long_version[i] is not None:
            cols.append("   " + long_version[i])
        else:
            cols.append("   " + "[incomplete installation]")
        print(" ".join(cols))
    print(usage)

if len(argv) == 2:
    if argv[1] in r_versions:
        path = argv[1]
    elif argv[1] in long_version:
        path = r_versions[long_version.index(argv[1])]
    else:
        try:
            i = int(argv[1])
            path = r_versions[i-1]
        except ValueError:
            print("ERROR: Input must be version number or index")
            exit(1)

    # check if already in use
    # check version is installed

    chdir(version_dir)
    if current is not None:
        unlink("Current")
    symlink(path, "Current")
    print("\nSwitched to version %s\n" % path)

