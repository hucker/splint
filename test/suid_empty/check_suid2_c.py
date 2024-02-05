
import src.splint as splint



def check_suid21_a():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")

def check_suid22_a():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")