"""
These the rc factory method allowing fairly easily to have various flavors or RC files to
be interchangeable.

"""

import pytest

from splint import SplintMarkup
from splint import splint_format


@pytest.mark.parametrize("tag,func,input,expected_output", [
    (splint_format.TAG_BOLD, SplintMarkup().bold, "Hello, World!", "<<b>>Hello, World!<</b>>"),
    (splint_format.TAG_ITALIC, SplintMarkup().italic, "Hello, World!", "<<i>>Hello, World!<</i>>"),
    (splint_format.TAG_UNDERLINE, SplintMarkup().underline, "Hello, World!", "<<u>>Hello, World!<</u>>"),
    (splint_format.TAG_STRIKETHROUGH, SplintMarkup().strikethrough, "Hello, World!", "<<s>>Hello, World!<</s>>"),
    (splint_format.TAG_CODE, SplintMarkup().code, "Hello, World!", "<<code>>Hello, World!<</code>>"),
    (splint_format.TAG_PASS, SplintMarkup().pass_, "Hello, World!", "<<pass>>Hello, World!<</pass>>"),
    (splint_format.TAG_FAIL, SplintMarkup().fail, "Hello, World!", "<<fail>>Hello, World!<</fail>>"),
    (splint_format.TAG_SKIP, SplintMarkup().skip, "Hello, World!", "<<skip>>Hello, World!<</skip>>"),
    (splint_format.TAG_WARN, SplintMarkup().warn, "Hello, World!", "<<warn>>Hello, World!<</warn>>"),
    (splint_format.TAG_EXPECTED, SplintMarkup().expected, "Hello, World!", "<<expected>>Hello, World!<</expected>>"),
    (splint_format.TAG_ACTUAL, SplintMarkup().actual, "Hello, World!", "<<actual>>Hello, World!<</actual>>"),
    (splint_format.TAG_RED, SplintMarkup().red, "Hello, World!", "<<red>>Hello, World!<</red>>"),
    (splint_format.TAG_BLUE, SplintMarkup().blue, "Hello, World!", "<<blue>>Hello, World!<</blue>>"),
    (splint_format.TAG_GREEN, SplintMarkup().green, "Hello, World!", "<<green>>Hello, World!<</green>>"),
    (splint_format.TAG_PURPLE, SplintMarkup().purple, "Hello, World!", "<<purple>>Hello, World!<</purple>>"),
    (splint_format.TAG_ORANGE, SplintMarkup().orange, "Hello, World!", "<<orange>>Hello, World!<</orange>>"),
    (splint_format.TAG_YELLOW, SplintMarkup().yellow, "Hello, World!", "<<yellow>>Hello, World!<</yellow>>"),
    (splint_format.TAG_BLACK, SplintMarkup().black, "Hello, World!", "<<black>>Hello, World!<</black>>"),
    (splint_format.TAG_WHITE, SplintMarkup().white, "Hello, World!", "<<white>>Hello, World!<</white>>"),
])
def test_all_tags(tag, func, input, expected_output):
    assert func(input) == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (SplintMarkup().bold, "Hello, World!", "Hello, World!"),
    (SplintMarkup().italic, "Hello, World!", "Hello, World!"),
    (SplintMarkup().underline, "Hello, World!", "Hello, World!"),
    (SplintMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (SplintMarkup().code, "Hello, World!", "Hello, World!"),
    (SplintMarkup().data, "Hello, World!", "Hello, World!"),
    (SplintMarkup().expected, "Hello, World!", "Hello, World!"),
    (SplintMarkup().actual, "Hello, World!", "Hello, World!"),
    (SplintMarkup().fail, "Hello, World!", "Hello, World!"),
    (SplintMarkup().warn, "Hello, World!", "Hello, World!"),
    (SplintMarkup().skip, "Hello, World!", "Hello, World!"),
    (SplintMarkup().pass_, "Hello, World!", "Hello, World!"),
    (SplintMarkup().red, "Hello, World!", "Hello, World!"),
    (SplintMarkup().blue, "Hello, World!", "Hello, World!"),
    (SplintMarkup().green, "Hello, World!", "Hello, World!"),
    (SplintMarkup().purple, "Hello, World!", "Hello, World!"),
    (SplintMarkup().orange, "Hello, World!", "Hello, World!"),
    (SplintMarkup().yellow, "Hello, World!", "Hello, World!"),
    (SplintMarkup().black, "Hello, World!", "Hello, World!"),
    (SplintMarkup().white, "Hello, World!", "Hello, World!")
])
def test_splint_render_text(markup_func, input, expected_output):
    render_text = splint_format.SplintRenderText()
    formatted_input = markup_func(input)
    assert render_text.render(formatted_input) == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (SplintMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (SplintMarkup().italic, "Hello, World!", "*Hello, World!*"),

    (SplintMarkup().strikethrough, "Hello, World!", "~~Hello, World!~~"),
    (SplintMarkup().code, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().pass_, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().fail, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().warn, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().skip, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().expected, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().actual, "Hello, World!", "`Hello, World!`"),
    # For color markups in markdown, we assume SplintBasicMarkdown 
    # does no formatting, hence the expected output is plain text.
    (SplintMarkup().red, "Hello, World!", "Hello, World!"),
    (SplintMarkup().blue, "Hello, World!", "Hello, World!"),
    (SplintMarkup().green, "Hello, World!", "Hello, World!"),
    (SplintMarkup().purple, "Hello, World!", "Hello, World!"),
    (SplintMarkup().orange, "Hello, World!", "Hello, World!"),
    (SplintMarkup().yellow, "Hello, World!", "Hello, World!"),
    (SplintMarkup().black, "Hello, World!", "Hello, World!"),
    (SplintMarkup().white, "Hello, World!", "Hello, World!"),
    (SplintMarkup().underline, "Hello, World!", "Hello, World!"),
])
def test_splint_basic_markdown(markup_func, input, expected_output):
    markdown_render = splint_format.SplintBasicMarkdown()
    formatted_input = markup_func(input)
    output = markdown_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (SplintMarkup().bold, "Hello, World!", "[bold]Hello, World![/bold]"),
    (SplintMarkup().italic, "Hello, World!", "[italic]Hello, World![/italic]"),
    (SplintMarkup().underline, "Hello, World!", "[u]Hello, World![/u]"),
    (SplintMarkup().strikethrough, "Hello, World!", "[strike]Hello, World![/strike]"),
    (SplintMarkup().code, "Hello, World!", "Hello, World!"),
    (SplintMarkup().pass_, "Hello, World!", "[green]Hello, World![/green]"),
    (SplintMarkup().fail, "Hello, World!", "[red]Hello, World![/red]"),
    (SplintMarkup().warn, "Hello, World!", "[orange]Hello, World![/orange]"),
    (SplintMarkup().skip, "Hello, World!", "[purple]Hello, World![/purple]"),
    (SplintMarkup().expected, "Hello, World!", "[green]Hello, World![/green]"),
    (SplintMarkup().actual, "Hello, World!", "[green]Hello, World![/green]"),
    (SplintMarkup().red, "Hello, World!", "[red]Hello, World![/red]"),
    (SplintMarkup().blue, "Hello, World!", "[blue]Hello, World![/blue]"),
    (SplintMarkup().green, "Hello, World!", "[green]Hello, World![/green]"),
    (SplintMarkup().purple, "Hello, World!", "[purple]Hello, World![/purple]"),
    (SplintMarkup().orange, "Hello, World!", "[orange]Hello, World![/orange]"),
    (SplintMarkup().yellow, "Hello, World!", "[yellow]Hello, World![/yellow]"),
    (SplintMarkup().black, "Hello, World!", "[black]Hello, World![/black]"),
    (SplintMarkup().white, "Hello, World!", "[white]Hello, World![/white]"),
])
def test_splint_basic_rich(markup_func, input, expected_output):
    rich_render = splint_format.SplintBasicRich()
    formatted_input = markup_func(input)
    output = rich_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (SplintMarkup().bold, "Hello, World!", "<b>Hello, World!</b>"),
    (SplintMarkup().italic, "Hello, World!", "<i>Hello, World!</i>"),
    (SplintMarkup().underline, "Hello, World!", "<u>Hello, World!</u>"),
    (SplintMarkup().strikethrough, "Hello, World!", "<s>Hello, World!</s>"),
    (SplintMarkup().code, "Hello, World!", "<code>Hello, World!</code>"),
    (SplintMarkup().pass_, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (SplintMarkup().fail, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (SplintMarkup().skip, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (SplintMarkup().warn, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (SplintMarkup().expected, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (SplintMarkup().actual, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (SplintMarkup().red, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (SplintMarkup().blue, "Hello, World!", '<span style="color:blue">Hello, World!</span>'),
    (SplintMarkup().green, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (SplintMarkup().purple, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (SplintMarkup().orange, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (SplintMarkup().yellow, "Hello, World!", '<span style="color:yellow">Hello, World!</span>'),
    (SplintMarkup().black, "Hello, World!", '<span style="color:black">Hello, World!</span>'),
    (SplintMarkup().white, "Hello, World!", '<span style="color:white">Hello, World!</span>'),
])
def test_splint_basic_html_renderer(markup_func, input, expected_output):
    html_renderer = splint_format.SplintBasicHTMLRenderer()
    formatted_input = markup_func(input)
    output = html_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func, input, expected_output", [
    (SplintMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (SplintMarkup().italic, "Hello, World!", "*Hello, World!*"),
    (SplintMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (SplintMarkup().code, "Hello, World!", "`Hello, World!`"),
    (SplintMarkup().pass_, "Hello, World!", ":green[Hello, World!]"),
    (SplintMarkup().fail, "Hello, World!", ":red[Hello, World!]"),
    (SplintMarkup().skip, "Hello, World!", ":purple[Hello, World!]"),
    (SplintMarkup().warn, "Hello, World!", ":orange[Hello, World!]"),
    (SplintMarkup().expected, "Hello, World!", ":green[Hello, World!]"),
    (SplintMarkup().actual, "Hello, World!", ":green[Hello, World!]"),
    (SplintMarkup().red, "Hello, World!", ":red[Hello, World!]"),
    (SplintMarkup().green, "Hello, World!", ":green[Hello, World!]"),
    (SplintMarkup().blue, "Hello, World!", ":blue[Hello, World!]"),
    (SplintMarkup().yellow, "Hello, World!", ":yellow[Hello, World!]"),
    (SplintMarkup().orange, "Hello, World!", ":orange[Hello, World!]"),
    (SplintMarkup().purple, "Hello, World!", ":purple[Hello, World!]"),
    (SplintMarkup().black, "Hello, World!", ":black[Hello, World!]"),
    (SplintMarkup().white, "Hello, World!", ":white[Hello, World!]"),

])
def test_splint_basic_streamlit_renderer(markup_func, input, expected_output):
    streamlit_renderer = splint_format.SplintBasicStreamlitRenderer()
    formatted_input = markup_func(input)
    output = streamlit_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func", [
    SplintMarkup().bold,
    SplintMarkup().italic,
    SplintMarkup().underline,
    SplintMarkup().strikethrough,
    SplintMarkup().code,
    SplintMarkup().pass_,
    SplintMarkup().fail,
    SplintMarkup().expected,
    SplintMarkup().actual,
    SplintMarkup().red,
    SplintMarkup().green,
    SplintMarkup().blue,
    SplintMarkup().yellow,
    SplintMarkup().orange,
    SplintMarkup().purple,
    SplintMarkup().black,
    SplintMarkup().white,
])
def test_splint_render_text_with_empty_string(markup_func):
    """All markups with null inputs should map to null outputs."""
    render_text = splint_format.SplintRenderText()
    input = ""
    expected_output = ""
    formatted_input = markup_func(input)
    output = render_text.render(formatted_input)
    assert output == expected_output
