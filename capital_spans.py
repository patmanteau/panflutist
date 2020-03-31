#!/usr/bin/env python
"""
Panflute filter for setting C A P I T A L text, with tracking. Use if []{.smallcaps}
is too weak.

Usage:

- In Pandoc markdown, use a bracketed Span of class allcaps: [TRAJAN]{.allcaps}
- The produced LaTeX output has several requirements:
  - The Microtype package for tracking (i.e., its \\textls and \\microtypecontext
    commands). In the preamble, load Microtype like so:
    \\usepackage{microtype}

  - A Microtype "allcaps" tracking context for tracking parameters. E.g.:
    \SetTracking[
      context = allcaps,
      spacing = {300*,,},
      outer spacing = {300*,,}
    ]{encoding={*}, shape=*}{70}

  - A \\textuppercase macro to do the grunt work of calling the proper commands:
    \\newcommand{\\textuppercase}[1]{%
      \\addfontfeatures{Numbers={Proportional,Lining}}%
      \\microtypecontext{tracking=allcaps}%
      \\textls{\\MakeUppercase{#1}}}%

  - The fontspec package to select proportional lining figures:
    \\usepackage{fontspec}

- For further information on Microtype's and fontspec's configuration,
  see their respective CTAN entries.
"""

from jinja2tex import latex_env
import panflute as pf

UPPERCASE = latex_env.from_string(r'\textuppercase{<< text >>}')


def action(e, doc):
    if isinstance(e, pf.Span) and 'allcaps' in e.classes:
        text = pf.stringify(e)
        if doc.format == 'latex':
            tex = UPPERCASE.render(text=text)
            return pf.RawInline(tex, format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
