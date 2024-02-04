
import src.splint as splint



def check_suid11():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")

def check_suid12():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")
