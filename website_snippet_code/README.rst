Website Snippet Code
====================

Adds code highlight snippet. Uses highlight.js library for syntax
highlighting.

By default, snippet uses automatic syntax detection. So no need to
specify which language is used (for supported syntaxes, see `web_highlight`
module).

If needed, it is possible to force specify which syntax is used if
for example, auto detection incorrectly guesses language (e.g. same
block of code could be interpreted by different languages).

To do that, there is snippet option `Syntax`, which allows to set wanted
syntax. There is also possibility to disable highlighting (if needed
for some reason), then simply select `No Highlighting` from a drop down.

Code is highlighted in read mode only. After saving edited website page,
it will refresh and code should become highlighted. When in edit mode,
once snippet is clicked to edit, it will go in `no highlight` mode and
will go back to highlight mode, once it is saved again (this is a
limitation, how Odoo handles edited blocks, which clash with the way
blocks are supposed to be highlighted).

Contributors
------------

* Andrius Laukavičius (timefordev)
