
import src.splint as splint



@splint.attributes(suid="suid11")
def check_suid11():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 11")

@splint.attributes(suid="suid12")
def check_suid12():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 12")

#### DUPLICATE SUID IN THIS MODULE
@splint.attributes(suid="suid12")
def check_suid13():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 12")

#### DUPLICATE SUID IN OTHER MODULE
def check_suid14():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 12")