#!/usr/bin/env python
r"""
Use KOMAscript's \addsec command for unnumbered sections.

Usage:

- Add the class unnumbered to headings. A single hyphen in an attribute
  context is equivalent. Also see pandoc's manual:
  https://pandoc.org/MANUAL.html#heading-identifiers

"""

from jinja2tex import latex_env
import panflute as pf

SECTION = latex_env.from_string(r'\addsec{<< text >>}')


def action(e, doc):
    if isinstance(e, pf.Header) and 'unnumbered' in e.classes:
        if doc.format == 'latex':
            text = pf.convert_text(
                pf.Plain(*e.content),
                extra_args=[
                    '--biblatex', '--filter=tools/panflutist/reference_spans.py'
                ],
                input_format='panflute',
                output_format='latex')
            tex = SECTION.render(text=text)
            return pf.RawBlock(tex, format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
