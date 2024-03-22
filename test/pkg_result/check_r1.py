from src import splint


@splint.attributes(ruid="pass11", tag='tag1')
def check_ruid11():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 11")


@splint.attributes(ruid="fail12", tag='tag1')
def check_ruid12():
    """Check RUID"""
    yield splint.SplintResult(status=False, msg="RUID 12")


@splint.attributes(ruid="skip_none", tag='tag1')
def check_ruid13():
    """Check RUID"""
    yield splint.SplintResult(status=None, msg="RUID 13")


@splint.attributes(ruid="skip_flag", tag='tag2')
def check_ruid14():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 14", skipped=True)


@splint.attributes(ruid="warning", tag='tag2')
def check_ruid15():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 15", warn_msg="This is a warning")


@splint.attributes(ruid="info", tag='tag2')
def check_ruid16():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="RUID 16", skipped=True, info_msg="This is an info")


@splint.attributes(ruid="blank_msg", tag='tag3')
def check_ruid17():
    """Check RUID"""
    yield splint.SplintResult(status=True, msg="", skipped=True, info_msg="")
