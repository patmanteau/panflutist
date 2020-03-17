#!/usr/bin/env python

"""
Make \\csquotes-style \\blockquotes
See also: https://github.com/nick-ulle/pandoc-minted

Usage:

- Add \usepackage{minted} to your LaTeX preamble
- For configuration options, see Minted's documentation: https://ctan.org/pkg/minted
- In Markdown, use a YAML code block (see http://scorreia.com/software/panflute/guide.html#yaml-code-blocks)::

    ``` blockquote
    identifier: linear-gradient-descent
    language: english
    cite: [@Perez_Python_2011, 13]
    ...
    Scientific computing, a discipline at the intersection of scientific research, engineering, 
    and computing, has traditionally focused either on raw performance (in languages such as
    Fortran and C/C++) or generality and ease of use (in systems such as Matlab or Mathematica),
    and mainly for numerical problems. Today, scientific researchers use computers for problems
    that extend far beyond pure numerics, and we need tools flexible enough to address issues
    beyond performance and usability. 
    ```

- Supported YAML options are identifier, caption and mintedopts. caption supports Markdown, including citations.
- Tag is 'python' instead of a generic 'code' to keep syntax highlighting in VS Code intact. The trade-off of having to
  extend the filter to support additional languages seems worth it to me.
"""

from jinja2tex import latex_env
import panflute as pf

TEMPLATE_BLOCKQUOTE = latex_env.from_string(r'\blockquote$citepre$citesuf{$text}')

def fenced_blockquote(options, data, element, doc, language):
    values = {
        'language': language,
        'mintedopts': '',
        'caption': '',
        'identifier': '',
        'text': data
    }

    caption = options.get('caption', '')
    if caption:
        converted_caption = pf.convert_text(caption, extra_args=['--biblatex'], input_format='markdown', output_format='latex')
        values['caption'] = r'\caption{{{}}}'.format(converted_caption)

    identifier = options.get('identifier', '')
    if identifier:
        values['identifier'] = r'\label{{{}}}'.format(identifier)

    mintedopts = options.get('mintedopts', '')
    if mintedopts:
        values['mintedopts'] = r'[{}]'.format(mintedopts)

    tex = TEMPLATE_CODEBLOCK.safe_substitute(values)
    return pf.RawBlock(tex, format='latex')

def blockquoted(options, data, element, doc):
    # We'll only run this for CodeBlock elements of class 'blockquoted'
    return fenced_blockquote(options, data, element, doc, language='blockquote')

def main(doc=None):
    return pf.run_filter(pf.yaml_filter, tag='blockquoted', function=fenced_python, doc=doc)

if __name__ == '__main__':
    main()
