import src.splint as splint


def test_yielder_do_something():
    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = splint.SplintYield()
        for i in [1, 2, 3]:
            yield from y(splint.SplintResult(status=False, msg=f"Msg {i}"))
        if not y.yielded:
            yield from y(splint.SR(status=True, msg="Nothing was to be done"))

    s_func = splint.SplintFunction(None, func1)

    ch = splint.SplintChecker(functions=[s_func])
    ch.pre_collect()
    ch.prepare()
    results = ch.run_all()

    assert len(results) == 3
    assert results[0].status is False
    assert results[0].msg == "Msg 1"
    assert results[1].status is False
    assert results[1].msg == "Msg 2"
    assert results[2].status is False
    assert results[2].msg == "Msg 3"


def test_yielder_counts():
    """
    This is tricky meta code.  The yield object is used to track how many passes
    and fails have been yielded because it is a common pattern to perform reporting
    based on all passes or all fails.  This test function runs through a simple
    scenario where it tests the counters in the yield object...and yields those
    results.

    """

    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = splint.SplintYield()
        yield from y(splint.SR(status=False, msg=f"Here's a fail"))
        yield from y(splint.SR(status=True, msg="Here's a pass"))
        yield from y(splint.SR(y.fail_count == 1 and y.pass_count == 1 and y.count == 2,
                               msg=f"Should be 1/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        yield from y(splint.SR(y.fail_count == 1 and y.pass_count == 2 and y.count == 3,
                               msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        yield from y(splint.SR(status=False, msg=f"Here's another fail"))
        yield from y(splint.SR(y.fail_count == 2 and y.pass_count == 3 and y.count == 5,
                               msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        p, f, t = y.counts
        yield from y(splint.SR(status=all((f == 2, p == 4, t == 6)), msg=f"Counts check {p}==1 and {f}==1 and {t}==5"))

    s_func = splint.SplintFunction("", func1)
    results = list(s_func())
    assert len(results) == 7
    assert results[0].status is False  # Hardcoded false
    assert results[1].status is True  # Hardcoded pass
    assert results[2].status is True  # verify counters
    assert results[3].status is True  # verify counters
    assert results[4].status is False  # verify y.counts
    assert results[5].status is True  # verify y.counts
    assert results[6].status is True  # verify y.counts


def test_yielder_do_nothing():
    """Verify that you can check if anything has happened"""

    def false():
        return False

    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func():
        y = splint.SplintYield()
        if false():
            yield from y(splint.SplintResult(status=False, msg="Done"))
        if not y.yielded:
            yield from y(splint.SR(status=True, msg="Nothing needed to be done."))

    s_func = splint.SplintFunction(None, func)

    ch = splint.SplintChecker(functions=[s_func])
    ch.pre_collect()
    ch.prepare()
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "Nothing needed to be done."
