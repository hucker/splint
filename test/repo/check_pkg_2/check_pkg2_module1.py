import src.splint as splint

@splint.attributes(tag="Pkg2")
def check_pkg_2_1():
    """Check Pkg 2-1"""
    return splint.SR(status=True, msg="Code from pkg1 checked 2-1")

@splint.attributes(tag="Pkg2")
def check_pkg_2_2():
    """Check Pkg 2-2"""
    return splint.SR(status=True, msg="Code from pkg2 checked 2-2")