from errno import *

###############################################################################
#
# Creation of a not-yet existent file with O_CREAT and O_EXCL
#
###############################################################################

# Open read-only
def subtest_1(ctx):
    """Create O_CREAT|O_EXCL|O_RDONLY"""
    f = ctx.no_file() + ctx.termslash()

    ctx.open_file(f, ro=1, crt=1, ex=1, read="")
    ctx.open_file(f, ro=1, crt=1, ex=1, err=EEXIST)
    ctx.open_file(f, ro=1, read="")

# Open write-only and overwrite
def subtest_2(ctx):
    """Create O_CREAT|O_EXCL|O_WRONLY"""
    f = ctx.no_file() + ctx.termslash()

    ctx.open_file(f, wo=1, crt=1, ex=1, write="q")
    ctx.open_file(f, ro=1, read="q")
    ctx.open_file(f, wo=1, crt=1, ex=1, err=EEXIST)
    ctx.open_file(f, ro=1, read="q")

# Open write-only and append
def subtest_3(ctx):
    """Create O_CREAT|O_EXCL|O_APPEND|O_WRONLY"""
    f = ctx.no_file() + ctx.termslash()

    ctx.open_file(f, app=1, crt=1, ex=1, write="q")
    ctx.open_file(f, ro=1, read="q")
    ctx.open_file(f, app=1, crt=1, ex=1, err=EEXIST)
    ctx.open_file(f, ro=1, read="q")

# Open read/write and overwrite
def subtest_4(ctx):
    """Create O_CREAT|O_EXCL|O_RDWR"""
    f = ctx.no_file() + ctx.termslash()

    ctx.open_file(f, rw=1, crt=1, ex=1, write="q")
    ctx.open_file(f, ro=1, read="q")
    ctx.open_file(f, rw=1, crt=1, ex=1, err=EEXIST)
    ctx.open_file(f, ro=1, read="q")

# Open read/write and append
def subtest_5(ctx):
    """Create O_CREAT|O_EXCL|O_APPEND|O_RDWR"""
    f = ctx.no_file() + ctx.termslash()

    ctx.open_file(f, ro=1, app=1, crt=1, ex=1, write="q")
    ctx.open_file(f, ro=1, read="q")
    ctx.open_file(f, ro=1, app=1, crt=1, ex=1, err=EEXIST)
    ctx.open_file(f, ro=1, read="q")
