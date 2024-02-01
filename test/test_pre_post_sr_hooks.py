import src.splint as splint


def test_result_pre_hook_result_only():
    """ Test that the pre hook changes the result"""
    @splint.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield splint.SplintResult(status=True,msg="It works")
    def result_hook1(_,sr):
        sr.status = False
        return sr
    def result_hook2(_,sr):
        sr.msg = "Hooked msg"
        return sr

    sfunc = splint.SplintFunction(None, hook_test,pre_sr_hooks=[result_hook1])
    for result in sfunc():
        assert result.status is False
        assert result.msg == "It works"

    sfunc = splint.SplintFunction(None, hook_test,pre_sr_hooks=[result_hook2])
    for result in sfunc():
        assert result.msg == "Hooked msg"
        assert result.status is True

def test_result_pre_hook_use_class():
    """ Test that the pre hook can use data from the SplintFunction class"""
    @splint.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield splint.SplintResult(status=True,msg="It works")

    def result_doc_string_to_msg(self:splint.SplintFunction,sr):
        """ Hook to change the doc string to the msg"""
        sr.msg = self.doc
        return sr

    sfunc = splint.SplintFunction(None, hook_test,pre_sr_hooks=[result_doc_string_to_msg])
    for result in sfunc():
        assert result.msg == "Hook Test Doc String"
        assert result.status is True


def test_verify_post_changes_pre():
    """ Test that the post hook changes the result from the pre hook"""
    @splint.attributes(tag="BoolOnly")
    def hook_test():
        """Hook Test Doc String"""
        yield splint.SplintResult(status=True,msg="It works")

    def result_pre(_,sr):
        """ Hard code sr"""
        sr.msg = "Pre Hook"
        sr.status = False
        return sr

    def result_post(_,sr):
        """ Hook to change the doc string to the msg"""
        sr.msg = "Post Hook"
        sr.status = True
        return sr

    sfunc = splint.SplintFunction(None, hook_test,pre_sr_hooks=[result_pre],post_sr_hooks=[result_post])
    for result in sfunc():
        assert result.msg == "Post Hook"
        assert result.status is True