from src import splint


def check_suid21_a():
    """No RUID"""
    yield splint.SplintResult(status=True, msg="No RUID")


def check_suid22_a():
    """No RUID"""
    yield splint.SplintResult(status=True, msg="No RUID")
