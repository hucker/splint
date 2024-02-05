
import src.splint as splint



@splint.attributes(suid="suid21")
def check_suid11_x():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 21")

@splint.attributes(suid="suid22")
def check_suid12_x():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 22")