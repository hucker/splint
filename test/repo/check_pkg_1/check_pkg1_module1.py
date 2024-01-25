import src.splint as splint

@splint.attributes(tag="Pkg1")
def check_pkg_1_1():
    """Check Pkg 1-1"""
    return splint.SR(status=True, msg="Code from pkg1 checked 1-1")

@splint.attributes(tag="Pkg1")
def check_pkg_1_2():
    """Check Pkg 1-2"""
    return splint.SR(status=True, msg="Code from pkg1 checked 1-2")