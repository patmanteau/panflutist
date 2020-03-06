#!/usr/bin/env python

r"""
Panflute filter that allows for acronyms in latex

Usage:

- Use Pandoc markdown bracketed Spans: [SO]{.ac d="Stack Overflow"}
- When outputting to latex, you must add this line to the preamble:
\usepackage[acronym,smallcaps]{glossaries}
- Then, this filter will add \newacronym{LRU}{LRU}{Least Recently Used}
  for the definition of LRU and finally \gls{LRU} to every time the term
  is used in the text.

(see https://groups.google.com/forum/#!topic/pandoc-discuss/Bz1cG55BKjM)
"""

from string import Template  # using .format() is hard because of {} in tex
import panflute as pf

TEMPLATE_GLS = Template(r"\gls{$acronym}")
TEMPLATE_NEWACRONYM = Template(r"\newacronym{$acronym}{$acronym}{$definition}")

def prepare(doc):
    doc.acronyms = {}

def action(e, doc):
    if isinstance(e, pf.Span) and 'ac' in e.classes:
        acronym = pf.stringify(e).lower()
        definition = e.attributes.get('d', '')
        # Only update dictionary if definition is not empty
        if definition:
            doc.acronyms[acronym] = definition

        if doc.format == 'latex':
            tex = TEMPLATE_GLS.safe_substitute(acronym=acronym)
            return pf.RawInline(tex, format='latex')

def finalize(doc):
    if doc.format == 'latex':
        tex = [r'\makeglossaries']
        for acronym, definition in doc.acronyms.items():
            tex_acronym = TEMPLATE_NEWACRONYM.safe_substitute(acronym=acronym, definition=definition)
            tex.append(tex_acronym)

        tex = [pf.MetaInlines(pf.RawInline(line, format='latex')) for line in tex]
        tex = pf.MetaList(*tex)
        if 'header-includes' in doc.metadata:
            doc.metadata['header-includes'].content.extend(tex)
        else:
            doc.metadata['header-includes'] = tex

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 

if __name__ == '__main__':
    main()
