#!/usr/bin/env python
r"""
Panflute filter supporting \textquote and \foreigntextquote in LaTeX

Issues: 
    - Nested parens with pandoc-citeproc

Usage:

- Use Pandoc markdown bracketed Spans: 
    - [Ganz Gallien ist von den Römern besetzt]{.textquote cite="[vgl. @Goscinny_Asterix_1967, 1\psqq]"}
    - [Toute la Gaule est occupée par les Romains]{.textquote lang="francais" punct="..." cite="[vgl. @Goscinny_Asterix_1967, 1\psqq]"}
- This filter will emit \{textquote/foreigntextquote}[<cite>][<punct>]{<text>} commands
"""

from jinja2tex import latex_env
import panflute as pf

QUOTE = latex_env.from_string(r"""
<%- if lang %>\foreigntextquote{<< lang >>}<% else %>\textquote<% endif -%>
<% if cite %>[{<< cite >>}]<% endif -%>
<% if punct %>[<< punct >>]<% endif -%>
{<< text >>}""")


def prepare(doc):
    pass


def action(e, doc):
    if isinstance(
            e, pf.Span) and doc.format == 'latex' and 'textquote' in e.classes:
        cite = e.attributes.get('cite')
        if cite:
            cite = pf.convert_text(cite,
                                   extra_args=['--biblatex'],
                                   input_format='markdown',
                                   output_format='latex')
        text = pf.convert_text(pf.Plain(e),
                               extra_args=['--biblatex'],
                               input_format='panflute',
                               output_format='latex')
        values = {
            'lang': e.attributes.get('lang'),
            'cite': cite,
            'punct': e.attributes.get('punct'),
            'text': text
        }
        tex = QUOTE.render(values)
        return pf.RawInline(tex, format='latex')

    else:
        return None


def finalize(doc):
    pass


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
