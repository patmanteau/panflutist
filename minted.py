#!/usr/bin/env python

r"""
Make generated LaTeX listings use Minted
See also: https://github.com/nick-ulle/pandoc-minted

Usage:

- Add \usepackage{minted} to your LaTeX preamble
- For configuration options, see Minted's documentation: https://ctan.org/pkg/minted
- In Markdown, use a YAML code block (see http://scorreia.com/software/panflute/guide.html#yaml-code-blocks)::

    ``` python
    identifier: linear-gradient-descent
    caption: Lineares Gradientenverfahren [vgl. @Cousteau, 33-35]
    floating: True
    mintedopts: linenos=false, mathescape
    ...
    def gradient_descent(X, y, theta, alpha, iterations):
        m = X.shape[0]
        J_it = np.zeros(iterations)
        
        for i in range(iterations):
            h_error = X.dot(theta) - y
            theta = theta - alpha * (1/m) * (np.transpose(X).dot(h_error))
            J_it[i] = compute_cost(X, y, theta)
            
        return (theta, J_it)
    ```

- Supported YAML options are identifier, caption and mintedopts. caption supports Markdown, including citations.
- Tag is 'python' instead of a generic 'code' to keep syntax highlighting in VS Code intact. The trade-off of having to
  extend the filter to support additional languages seems worth it to me.
"""

from string import Template  # using .format() is hard because of {} in tex
import panflute as pf

TEMPLATE_FLOATING_CODEBLOCK = Template(r"""\begin{listing}[htbp]
\begin{minted}$mintedopts{$language}
$text
\end{minted}
$caption
$identifier
\end{listing}""")

TEMPLATE_CODEBLOCK = Template(r"""{%
\singlespacing
\begin{minted}$mintedopts{$language}
$text
\end{minted}
\unskip
$caption
$identifier
}""")

def fenced_code(options, data, element, doc, language):
    values = {
        'language': language,
        'mintedopts': '',
        'caption': '',
        'identifier': '',
        'text': data
    }

    identifier = options.get('identifier', '')
    if identifier:
        values['identifier'] = r'\label{{{}}}'.format(identifier)

    mintedopts = options.get('mintedopts', '')
    if mintedopts:
        values['mintedopts'] = r'[{}]'.format(mintedopts)

    caption = options.get('caption', '')
    floating = options.get('floating', True)#.strip().lower() == 'true'
    if floating:
        if caption:
            converted_caption = pf.convert_text(caption, extra_args=['--biblatex'], input_format='markdown', output_format='latex')
            values['caption'] = r'\caption{{{}}}'.format(converted_caption)
        tex = TEMPLATE_FLOATING_CODEBLOCK.safe_substitute(values)
        return pf.RawBlock(tex, format='latex')
    else:
        if caption:
            converted_caption = pf.convert_text(caption, extra_args=['--biblatex'], input_format='markdown', output_format='latex')
            values['caption'] = r'\captionof{{listing}}{{{}}}'.format(converted_caption)
        tex = TEMPLATE_CODEBLOCK.safe_substitute(values)
        return pf.RawBlock(tex, format='latex')
    
def fenced_python(options, data, element, doc):
    # We'll only run this for CodeBlock elements of class 'python'
    if doc.format == 'latex':
        return fenced_code(options, data, element, doc, language='python')

def main(doc=None):
    return pf.run_filter(pf.yaml_filter, tag='python', function=fenced_python, doc=doc)

if __name__ == '__main__':
    main()
