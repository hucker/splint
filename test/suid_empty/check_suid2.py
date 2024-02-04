
import src.splint as splint



def check_suid21():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")

def check_suid22():
    """No SUID"""
    yield splint.SplintResult(status=True,msg="No SUID")