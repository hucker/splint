
import src.splint as splint



@splint.attributes(suid="suid11")
def check_suid11_x():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 11")

@splint.attributes(suid="suid12")
def check_suid12_x():
    """Check SUID"""
    yield splint.SplintResult(status=True,msg="SUID 12")
