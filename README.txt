PyElly is a rule-based natural language processing tool that has been
around for forty years in various incarnations. It has come in handy many
times in my career as a computational linguist; and so I am making it
available to anyone needing support to process or pre-process text data.

PyElly provides flexible tokenization, syntax-driven parsing, English
inflectional and morphological stemming, macro substitutions, basic
entity extraction, ambiguity handling, and a general procedural framework
for translation.

The latest version has been completely rewritten in mostly object-oriented
Python. It has now passed alpha testing and may be downloaded in a beta
release from Github. Go to https://github.com/prohippo/pyelly.git .

For information on how to use PyElly, see the PyEllyManual.pdf file in the
same directory as this README.txt file. Documentation of individual Python
source files can be obtained with the Python pydoc utility.

At present, PyElly consists of 57 Python modules comprising about 15
thousand lines of source code. Included also are various definition
files to support basic English-language capabilities and various examples
of rule files defining simple applications for integration testing. For
example,

* indexing - remove stopwords and get stems for content words from raw
             text input.
* texting  - readable text compression.
* doctor   - emulation of Weizenbaum's Doctor program.
* chinese  - simple translation of English to simplified and
             traditional Chinese characters.
* querying - translate English questions to SQL queries.
* disambig - disambiguation with WordNet information.

The disambig application is still under development. Others may be included
in the PyElly package as well and will be uploaded to github when available.

PyElly is being released under a BSD license. Be advised that this all is
currently beta software and will be changing until release v1.0.

Release Notes:

 0.1  - 25dec2013  initial release
 0.2  - 16mar2014  increase number of syntactic categories to 64
                   add storing and reinserting of deleted output buffer text
                   fix bugs in DELETE TO generative semantic command
                   add unit testing input to PyElly distribution
                   save integration testing script doTest properly
                   eliminate inconsistencies in integration testing keys
                   improve output of unit test for generativeProcedure.py
 0.3  - 24apr2014  extend generative semantics to support new applications
                   add UNITE, INTERSECT, COMPLEMENT, UNCAPITALIZE
                   add QUEUE, UNQUEUE, SHOW
                   replace DELETE ALL
                   make STORE more efficient and generalize, fix bugs
                   allow for initializing of global variables in grammar
                   strengthen unit testing
                   add querying application for integration testing
0.4   - 04jul2014  add support for conceptual hierarchies in cognitive semantics
                   separate lookup tables for syntactic and semantic features
                   fix bugs in loading vocabulary tables from text definitions
                   fix bugs in load conceptual hierarchies from text definitions
                   improve unit testing
                   add core of disambig application for integration testing

Versions will reflect changes in PyElly code, which may require deleting and
regenerating older *.elly.bin files to ensure correct operation. Changes to
PyElly example application files, unit testing input files, or documentation
will be made from time to time, but this will leave version numbers unchanged.
