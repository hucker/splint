import src.splint as splint


@splint.attributes(ruid="suid21")
def check_suid21_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 21")


@splint.attributes(ruid="suid22")
def check_suid122_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 22")


@splint.attributes(ruid="suid22")
def check_suid23_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 23")
