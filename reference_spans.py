#!/usr/bin/env python

"""
Easy references to tables, images etc.

Usage:

- In Pandoc markdown, use a bracketed Span of class ref: [ref_img_trajan]{.ref}

"""

from string import Template  # using .format() is hard because of {} in tex
import panflute as pf

TEMPLATE_LSUPPER = Template(r'\ref{$text}')

def action(e, doc):
    if isinstance(e, pf.Span) and 'ref' in e.classes:
        text = pf.stringify(e).replace('#', '')
        if doc.format == 'latex':
            tex = TEMPLATE_LSUPPER.safe_substitute(text=text)
            return pf.RawInline(tex, format='latex')

def main(doc=None):
    return pf.run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()
