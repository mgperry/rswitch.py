#!/usr/local/bin/python3
from plistlib import load, InvalidFileException
from os.path import dirname, basename, realpath, join, isdir, islink, abspath
from os import walk, symlink, unlink
from sys import argv, stdin, exit
from re import match
from argparse import ArgumentParser, ArgumentTypeError

is_int = lambda x: match(r"^\d+$", x) is not None

class RVersion:
    def __init__(self, folder):
        self.version = basename(folder)
        self.r_home = dirname(folder)
        try:
            fn = open(join(folder, "Resources", "Info.plist"), 'rb')
            pl = load(fn)
            self.long = pl["CFBundleVersion"]
        except (FileNotFoundError, InvalidFileException):
            self.long = None
        current = basename(realpath(join(dirname(folder), "Current")))
        self.in_use = (current == self.version)

    def __str__(self):
        v = self.version
        if self.in_use:
            v = "=> " + v
        v = v.rjust(8)
        l = "   " + (self.long or "[incomplete installation]")
        return v + l

    def switch(self):
        if self.in_use:
            print("\nVersion %s already in use." % self.version)
        else:
            current = join(self.r_home, "Current")
            islink(current) and unlink(current)
            symlink(self.version, current)
            print("\nSwitched to version %s" % self.version)

        if self.long is None:
            print("\nWARNING: Current R version does not appear to be correctly installed")

    def has_version(self, v):
        if self.version == v:
            return True
        elif self.long ==v:
            return True
        elif v[0:3] == self.version:
            msg = "\nVersion %s is not installed, however R %s is still available as version %s."
            print(msg % (v, v[0:3], self.long))
            print("\nSwitch to version %s? [Y/n]" % self.long)
            answer = stdin.read(1)
            if answer in ["Y", "y", "\n"]:
                return True

        return False


def version_info(lst):
    print("\nAvalable versions:\n")
    for i, r in enumerate(lst):
        print("[{0}]".format(i+1).rjust(8), end="")
        print(r)

def IndexOrVersion(v):
    try:
        return match("(\d)(\.\d)?(\.\d)?", v).group(0)
    except:
        raise ArgumentTypeError("Argument must be index or version (x.y[.z])")

if __name__ == "__main__":
    parser = ArgumentParser(description='Switch R Version.')
    parser.add_argument("v", type=IndexOrVersion, nargs="?")
    args = parser.parse_args()

    version_dir = "/Library/Frameworks/R.framework/Versions/"
    if not isdir(version_dir):
        print("\n%s is not a directory.\n" % version_dir)
        exit(1)

    r_versions = [RVersion(join(version_dir, x)) for x in next(walk(version_dir))[1] if x != "Current"]
    r_versions.sort(key=lambda x: x.version)

    if len(r_versions) == 0:
        print("\nNo R versions found in %s\n" % version_dir)
        exit(0)

    if not any([x.in_use for x in r_versions]):
        print("\nNB: No Current version in use.")

    v = args.v

    if v is None:
        version_info(r_versions)
        print("\nUsage: rswitch [index|version]")
        print("")
        exit(0)

    if is_int(v):
        if int(v) < 1:
            print("\nERROR: Index must be a positive integer.\n")
            exit(1)
        try:
            r = r_versions[int(v)-1]
        except IndexError:
            print("\nThere are not that many versions of R installed. Available versions are:")
            version_info(r_versions)
            print("")
            exit(0)
    else:
        r = next(filter(lambda x: x.has_version(v), r_versions), None)

    if r is not None:
        r.switch()
    else:
        print("\nVersion %s is not installed. Available versions are:" % v)
        version_info(r_versions)

    print("")
    exit(0)

