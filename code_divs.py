#!/usr/bin/env python
r"""
Make generated LaTeX listings use Minted
See also: https://github.com/nick-ulle/pandoc-minted

Usage:

- Add \usepackage{minted} to your LaTeX preamble
- For configuration options, see Minted's documentation: 
  https://ctan.org/pkg/minted
- In Markdown, use a YAML code block (see
  http://scorreia.com/software/panflute/guide.html#yaml-code-blocks):

    ``` python
    language: python
    identifier: linear-gradient-descent
    caption: Lineares Gradientenverfahren [vgl. @Cousteau, 33-35]
    floating: True
    placement: htp
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

- Supported YAML options are identifier, caption and mintedopts. caption
  supports Markdown, including citations.
- Tag is 'python' instead of a generic 'code' to keep syntax highlighting
  in VS Code intact. The trade-off of having to extend the filter to support
  additional languages seems worth it to me.
"""

from jinja2tex import latex_env
import panflute as pf

TEMPLATE_FLOATING_CODEBLOCK = latex_env.from_string(r"""\begin{listing}[htbp]
\begin{minted}$mintedopts{$language}
$text
\end{minted}
$caption
$identifier
\end{listing}""")

TEMPLATE_CODEBLOCK = latex_env.from_string(r"""{%
\singlespacing
\begin{minted}$mintedopts{$language}
$text
\end{minted}
%\unskip
$caption
$identifier
}""")
CODEBLOCK = latex_env.from_string(r"""<%- if floating -%>
\begin{listing}<% if placement %>[<< placement >>]<% endif %>
<%- endif -%>
\begin{minted}<% if options %>[<< options >>]<% endif %>{<< language >>}
<< content >>
\end{minted}
<% if caption %><% if floating %>\caption{<< caption >>}<% else %>\captionof{listing}{<< caption >>}<% endif %><% endif %>
<% if identifier %>\label{<< identifier >>}<% endif %>
<% if floating %>\end{listing}<% endif %>""")


def fenced_latex(options, data, element, doc):
    raw_caption = options.get('caption')
    caption = pf.convert_text(options.get('caption'),
                              extra_args=['--biblatex'],
                              input_format='markdown',
                              output_format='latex') if raw_caption else None

    latex = CODEBLOCK.render({
        'floating': options.get('caption'),
        'placement': options.get('placement'),
        'options': options.get('mintedopts'),
        'language': options.get('language'),
        'content': data,
        'caption': caption,
        'identifier': options.get('identifier', '')
    })
    return pf.RawBlock(latex, format='latex')


def fenced_html(options, data, element, doc):
    identifier = options.get('identifier', '')
    element.identifier = identifier
    caption = options.get('caption', '')
    caption = pf.convert_text(caption,
                              extra_args=['--biblatex'],
                              input_format='markdown',
                              output_format='html')

    caption_span = pf.Plain(
        pf.Span(pf.RawInline(caption), classes=['fencedSourceCodeCaption']))
    code_block = pf.CodeBlock(data,
                              classes=element.classes,
                              attributes=element.attributes)

    return pf.Div(code_block,
                  caption_span,
                  identifier=identifier,
                  classes=['fencedSourceCode'])


def fenced_listing(options, data, element, doc):
    # We'll only run this for CodeBlock elements of class 'python'
    if doc.format == 'latex':
        return fenced_latex(options, data, element, doc)
    elif doc.format == 'html':
        return fenced_html(options, data, element, doc)


def main(doc=None):
    return pf.run_filter(pf.yaml_filter,
                         doc=doc,
                         tags={
                             'python': fenced_listing,
                             'bash': fenced_listing,
                             'sql': fenced_listing
                         })


if __name__ == '__main__':
    main()
