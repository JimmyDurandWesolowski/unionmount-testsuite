#
# Create and set up a lower layer for the test scripts to use
#
from tool_box import *
import os, shutil, sys

def create_file(name, content):
    fd = open(name, "w")
    fd.write(content)
    fd.close()

def set_up(ctx):
    cfg = ctx.config()
    lower_mntroot = cfg.lower_mntroot()
    lowerdir = cfg.lowerdir()
    testdir = cfg.testdir()

    if sys.version_info[0] == 2:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.sync()
    else:
        os.sync()

    # Discard anything already mounted on the mountpoint to avoid contamination
    # as unionmount tries to collect all the mounts located there into the
    # union.
    if cfg.testing_unionmount():
        try:
            while system("umount " + cfg.union_mntroot() + " >&/dev/null"):
                pass
        except RuntimeError:
            pass

    if cfg.testing_overlayfs():
        try:
            while system("grep 'lower_layer " + lower_mntroot + "' /proc/mounts >/dev/null" +
                         " && umount " + lower_mntroot):
                pass
        except RuntimeError:
            pass
        try:
            while system("grep 'upper_layer " + cfg.upper_mntroot() + "' /proc/mounts >/dev/null" +
                         " && umount " + cfg.upper_mntroot()):
                pass
        except RuntimeError:
            pass
        try:
            while system("grep 'overlayfs " + cfg.union_mntroot() + "' /proc/mounts >/dev/null" +
                         " && umount " + cfg.union_mntroot()):
                pass
        except RuntimeError:
            pass

    # Create a lower layer to union over
    if not os.path.exists(lower_mntroot):
        os.makedirs(lower_mntroot)
    system("mount -t tmpfs lower_layer " + lower_mntroot)

    # Systemd has weird ideas about things
    system("mount --make-private " + lower_mntroot)

    #
    # Create a few test files we can use in the lower layer
    #
    os.mkdir(lowerdir)

    pieces = testdir.split("/")
    del pieces[0]
    path = ""
    for i in pieces:
        path += "/" + i
        ctx.record_file(path, "d")
    ctx.set_cwd(testdir)

    for i in range(100, 130):
        si = str(i)

        # Under the test directory, we create a bunch of regular files
        # containing data called foo100 to foo129:
        create_file(lowerdir + "/foo" + si, ":xxx:yyy:zzz")
        rec = ctx.record_file("foo" + si, "r")

        # Then we create a bunch of direct symlinks to those files
        to = "../a/foo" + si
        os.symlink(to, lowerdir + "/direct_sym" + si)
        rec = ctx.record_file("direct_sym" + si, "s", to, rec)

        # Then we create a bunch of indirect symlinks to those files
        to = "direct_sym" + si
        os.symlink(to, lowerdir + "/indirect_sym" + si)
        ctx.record_file("indirect_sym" + si, "s", to, rec)

        # Then we create a bunch symlinks that don't point to extant files
        to = "no_foo" + si
        os.symlink(to, lowerdir + "/pointless" + si)
        rec = ctx.record_file("no_foo" + si, None)
        ctx.record_file("pointless" + si, "s", to, rec)

        # We create a bunch of directories, each with an empty file
        # and a populated subdir
        os.mkdir(lowerdir + "/dir" + si)
        rec = ctx.record_file("dir" + si, "d")
        create_file(lowerdir + "/dir" + si + "/a", "")
        ctx.record_file("dir" + si + "/a", "f")

        os.mkdir(lowerdir + "/dir" + si + "/pop")
        ctx.record_file("dir" + si + "/pop", "d")
        create_file(lowerdir + "/dir" + si + "/pop/b", ":aaa:bbb:ccc")
        ctx.record_file("dir" + si + "/pop/b", "f")
        os.mkdir(lowerdir + "/dir" + si + "/pop/c")
        ctx.record_file("dir" + si + "/pop/c", "d")

        # And add direct and indirect symlinks to those
        to = "../a/dir" + si
        os.symlink(to, lowerdir + "/direct_dir_sym" + si)
        rec = ctx.record_file("direct_dir_sym" + si, "s", to, rec)
        #ctx.record_file("direct_dir_sym" + si + "/a", "f")

        to = "direct_dir_sym" + si
        os.symlink(to, lowerdir + "/indirect_dir_sym" + si)
        ctx.record_file("indirect_dir_sym" + si, "s", to, rec)
        #ctx.record_file("indirect_dir_sym" + si + "/a", "f")

        # And a bunch of empty directories
        os.mkdir(lowerdir + "/empty" + si)
        ctx.record_file("empty" + si, "d")

        # Everything above is then owned by the bin user
        for f in [ "foo", "direct_sym", "indirect_sym", "pointless" ]:
            os.lchown(lowerdir + "/" + f + si, 1, 1)

        # Create some root-owned regular files also
        create_file(lowerdir + "/rootfile" + si, ":xxx:yyy:zzz")
        ctx.record_file("rootfile" + si, "r")

        # Non-existent dir
        ctx.record_file("no_dir" + si, None)

    # The mount has to be read-only for us to make use of it
    system("mount -o remount,ro " + lower_mntroot)
    ctx.note_lower_fs(lowerdir)
