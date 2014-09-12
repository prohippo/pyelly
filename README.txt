PyElly is a rule-based natural language processing tool that has been
around for forty years in various incarnations. It supports quick
development of many kinds of applications by taking care of low-level
details not central to a given problem. It is now freely available on
the web to anyone needing to process or pre-process text data.

PyElly provides flexible tokenization, syntax-driven parsing, English
inflectional and morphological stemming, macro substitutions, basic
and extended entity extraction, ambiguity handling, sentence recognition,
support for large external dictionaries, and a general procedural
framework for translation from UTF-8 to UTF-8.

The latest version has been completely rewritten in mostly object-oriented
Python. It has now passed multiple stages of beta testing and may be
downloaded from Github at https://github.com/prohippo/pyelly.git . The
latest release is v0.5.1beta.

To learn how to use PyElly, see the PyEllyManual.pdf file in the same
directory as this README.txt file. This has 96 pages of information,
including an overview of some basic linguistics. Documentation of
individual Python source files can be generated as needed with the Python
pydoc utility.

At present, PyElly consists of 58 Python modules comprising about 16
thousand lines of source code. Included also are various definition
files to support basic English-language capabilities and various sample
applications, including

* indexing - remove stopwords and get stems for content words from raw
             text input.
* texting  - readable text compression.
* doctor   - emulation of Weizenbaum's Doctor program.
* chinese  - basic translation of English to simplified or
             traditional Chinese characters.
* querying - rewrite English questions as SQL queries for a Soviet
             aircraft database.
* disambig - disambiguation of phrases with WordNet information.

These illustrate what you can do with PyElly and also serve as a basis for
comprehensive integration testing.  Other applications will be added to the
PyElly package on Github in the future. You may use them as models for
building your own systems.

PyElly is being released under a BSD license. Be advised that the current 
beta software and documentation is still evolving. The first stable release
will be v1.0, which should be ready in late 2014.

Release Notes:

 0.1    -  25dec2013  initial beta release
 0.2    -  16mar2014  increase number of syntactic categories to 64
                      add storing and reinserting of deleted output buffer text
                      fix bugs in DELETE TO generative semantic command
                      add unit testing input to PyElly distribution
                      save integration testing script doTest properly
                      eliminate inconsistencies in integration testing keys
                      improve output of unit test for generativeProcedure.py
 0.3    -  24apr2014  extend generative semantics to support new applications
                      add UNITE, INTERSECT, COMPLEMENT, UNCAPITALIZE
                      add QUEUE, UNQUEUE, SHOW
                      replace DELETE ALL code
                      make STORE more efficient and generalize, fix bugs
                      allow for initializing of global variables in grammar
                      strengthen unit testing, add querying integration test
 0.4    -  04jul2014  support conceptual hierarchies in cognitive semantics
                      separate lookup tables for syntactic and semantic features
                      fix bugs in loading vocabulary tables from text input
                      fix bugs in load conceptual hierarchies from text input
                      improve unit testing
                      add core of disambig application for integration testing
 0.4.1  -  13aug2014  clean up and flesh out disambig application
                      fix bugs in cognitive semantics
                      fix bugs in conceptual hierarchies
                      miscellaneous cleanup of Python source files
                      improve unit testing of modules, parse tree dump
 0.5    -  01sep2014  simplify doTest and make parse tree dumps easier to filter
                      add audit on usage of grammar symbols for error checking
                      add version check when loading saved binary language files
                      define ellyException to handle errors in table loading
                      add error messages when generating language tables
                      simplify semantic feature check by generative semantics
                      extend generative semantic unit tests
                      add bad application to test error reporting
 0.5.1  -  12sep2014  fix problems with error reporting and recovery
                      extend bad application for integration testing

New versions will reflect major changes in PyElly code. This typically will require
regeneration of any previously saved *.elly.bin files to ensure correct operation.
Changes only to PyElly example application files, unit testing input files, or
documentation will be made from time to time, but these will leave version numbers
unchanged.
