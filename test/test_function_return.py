from src import splint


def test_simple_return_function():
    """ Test cases for checking that test functions (rather than generators) work as expected. """

    @splint.attributes(tag="Return")
    def return_not_yield():
        """Test Function With Return"""
        return splint.SR(status=True, msg="It works with return", info_msg="This uses return")

    sfunc = splint.SplintFunction(return_not_yield)

    for result in sfunc():
        assert result.func_name == "return_not_yield"
        assert result.status is True
        assert result.msg == "It works with return"
        assert result.doc == "Test Function With Return"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == "This uses return"
        assert result.tag == "Return"


def test_multiple_return_function():
    """ Test cases for checking that test functions returning a list works. """

    @splint.attributes(tag="Return")
    def returns_not_yield():
        """Test Function With Returns"""
        return [splint.SR(status=True, msg="It works with return1", info_msg="This uses return1"),
                splint.SR(status=True, msg="It works with return2", info_msg="This uses return2")]

    sfunc = splint.SplintFunction(returns_not_yield)

    for count, result in enumerate(sfunc(), start=1):
        assert result.func_name == "returns_not_yield"
        assert result.status is True
        assert result.msg == f"It works with return{count}"
        assert result.doc == "Test Function With Returns"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == f"This uses return{count}"
        assert result.tag == "Return"


def test_boolean_only_return_function():
    """ Test cases that allows for only returning a boolean. """

    @splint.attributes(tag="BoolOnly")
    def return_boolean_only():
        """Test Function that returns a boolean"""
        return True

    sfunc = splint.SplintFunction(return_boolean_only)

    for result in sfunc():
        assert result.func_name == "return_boolean_only"
        assert result.status is True
        assert result.doc == """Test Function that returns a boolean"""
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.tag == "BoolOnly"
        assert result.count == 1


def test_boolean_only_yield_function():
    """ Test cases that allows for only returning a boolean. """

    @splint.attributes(tag="BoolOnly")
    def yield_boolean_only():
        """Test Function that yields a boolean True"""
        yield True

    sfunc = splint.SplintFunction(yield_boolean_only)

    for result in sfunc():
        assert result.func_name == "yield_boolean_only"
        assert result.status is True
        assert result.doc == """Test Function that yields a boolean True"""
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.tag == "BoolOnly"
        assert result.count == 1


def test_boolean_only_yield_function_fail():
    """ Test cases that allows for only returning a boolean. """

    @splint.attributes(tag="BoolOnly")
    def yield_boolean_only_fail():
        """Test Function that yields a boolean False"""
        yield False

    sfunc = splint.SplintFunction(yield_boolean_only_fail, None)

    for result in sfunc():
        assert result.func_name == "yield_boolean_only_fail"
        assert result.status is False
        assert result.doc == """Test Function that yields a boolean False"""
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.tag == "BoolOnly"
        assert result.count == 1
