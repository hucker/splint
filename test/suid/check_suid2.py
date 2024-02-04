
import src.splint as splint



@splint.attributes(suid="suid21")
def check_suid11():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 21")

@splint.attributes(suid="suid22")
def check_suid12():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 22")