PyElly is a rule-based natural language processing tool that has been
around for forty years in various incarnations. It has come in handy many
times in my career as a computational linguist; and so I am making it
available to anyone else needing to process or pre-process text data.

PyElly provides flexible tokenization, syntax-driven parsing, English
inflectional and morphological stemming, macro substitutions, basic
entity extraction, ambiguity handling, and a general procedural framework
for translation.

The latest version has been completely rewritten in mostly object-oriented
Python. It has now passed alpha testing and may be downloaded in a beta
release from Github. Go to https://github.com/prohippo/pyelly.git .

For information on how to use PyElly, read the PyEllyManual.pdf file in the
same directory as this README file. Documentation of individual Python
source files can be obtained with the Python pydoc utility.

At present, PyElly consists of 57 Python modules comprising about 15
thousand lines of source code. Included also are various separate definition
files to support basic English-language capabilities and various examples
of rule files defining simple applications for integration testing. For
example,

* indexing - remove stopwords and get stems for content words from raw
             text input.
* texting  - readable text compression.
* doctor   - emulation of Weizenbaum's Doctor program.
* chinese  - demonstration of simple translation to simplified and
             traditional characters.

It is expected that beta development will include two more example
applications for the integration test suite: a translator of natural language
queries into SQL and a semantic disambiguation demonstration.  These will be
uploaded to Github upon their completion.

PyElly is being released under a BSD license. Be advised that this all is
currently beta software.
