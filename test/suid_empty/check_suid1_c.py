
import src.splint as splint



def check_suid11_a():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")

def check_suid12_a():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")
