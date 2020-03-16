#!/usr/bin/env python

r"""
Panflute filter supporting acronyms and glossary entries in latex

Usage:

- Use Pandoc markdown bracketed Spans: 
    - [so]{.ac short="SO" long="Stack Overflow"}
    - [ptt]{.gl .up name="Potato" text="potato" description="Starchy tuber" plural="potatoes"}
- When outputting to latex, you must add this line to the preamble:
\usepackage[acronym,smallcaps]{glossaries-extra}
- Then, this filter will add \newacronym{LRU}{LRU}{Least Recently Used}
  for the definition of LRU and finally \gls{LRU} to every time the term
  is used in the text.

(see https://groups.google.com/forum/#!topic/pandoc-discuss/Bz1cG55BKjM)
"""

from jinja2 import Template  # using .format() is hard because of {} in tex
from jinja2tex import latex_env
import panflute as pf

USE_TERM = latex_env.from_string(
    r"<% if uppercase %>\Gls<% else %>\gls<% endif %>{<< label >>}"
)

DEFINE_ABBREVIATION = latex_env.from_string(
    r"\newabbreviation{<< label >>}{<< short >>}{<< long >>}"
)

DEFINE_GLOSSARY_ENTRY = latex_env.from_string(r"""
\newglossaryentry{<< label >>}{
    name={<< name >>},
    <% if text %>text={<< text >>},<% endif %>
    <% if plural %>plural={<< plural >>},<% endif %>
    description={<< description >>}
}
""")

def prepare(doc):
    doc.abbrs = {}
    doc.glsentries = {}

def ac_latex(e, doc):
    label = pf.stringify(e).lower()
    _short = e.attributes.get('short')
    _long = e.attributes.get('long')

    if _short and _long:
        values = {
            'label': label,
            'short': _short,
            'text': _long,
            'uppercase': 'up' in e.classes
        }
        doc.abbrs[label] = values
    
    tex = USE_TERM.render(label=label)
    return pf.RawInline(tex, format='latex')

def gl_latex(e, doc):
    label = pf.stringify(e).lower()
    name = e.attributes.get('name')
    description = e.attributes.get('description')
    
    if label and name and description:
        values = {
            'label': label,
            'name': name,
            'description': pf.convert_text(description, extra_args=['--biblatex'], input_format='markdown', output_format='latex'),
            'text': e.attributes.get('text'),
            'plural': e.attributes.get('plural'),
            'uppercase': 'up' in e.classes
        }
        doc.glsentries[label] = values

    tex = USE_TERM.render(label=label)
    return pf.RawInline(tex, format='latex')

def action(e, doc):
    if isinstance(e, pf.Span) and doc.format == 'latex':
        if 'ac' in e.classes:
            return ac_latex(e, doc)
        elif 'gl' in e.classes:
            return gl_latex(e, doc)
    else:
        return None

def finalize(doc):
    if doc.format == 'latex':
        tex = [r'\makeglossaries']
        for _, values in doc.abbrs.items():
            tex_acronym = DEFINE_ABBREVIATION.render(**values)
            tex.append(tex_acronym)

        for _, values in doc.glsentries.items():
            tex_acronym = DEFINE_GLOSSARY_ENTRY.render(**values)
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
