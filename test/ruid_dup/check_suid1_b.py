from src import splint


@splint.attributes(ruid="suid11")
def check_suid11_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 11")


@splint.attributes(ruid="suid12")
def check_suid12_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 12")


#### DUPLICATE RUID IN THIS MODULE
@splint.attributes(ruid="suid12")
def check_suid13_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 12")


#### DUPLICATE RUID IN OTHER MODULE
def check_suid14_d():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 12")
