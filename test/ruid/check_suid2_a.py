from src import splint


@splint.attributes(ruid="suid21")
def check_suid11_x():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 21")


@splint.attributes(ruid="suid22")
def check_suid12_x():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 22")
