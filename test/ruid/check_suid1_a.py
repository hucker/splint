from src import splint


@splint.attributes(ruid="suid11")
def check_suid11_x():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 11")


@splint.attributes(ruid="suid12")
def check_suid12_x():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 12")
