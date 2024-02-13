import src.splint as splint


def check_suid11_a():
    """No RUID"""
    yield splint.SplintResult(status=True, msg="No RUID")


def check_suid12_a():
    """No RUID"""
    yield splint.SplintResult(status=True, msg="No RUID")
