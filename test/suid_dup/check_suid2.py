
import src.splint as splint



@splint.attributes(suid="suid21")
def check_suid21():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 21")

@splint.attributes(suid="suid22")
def check_suid122():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 22")

@splint.attributes(suid="suid22")
def check_suid23():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 23")

