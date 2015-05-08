PyElly is a rule-based natural language processing tool that has existed
for over forty years in various incarnations. It can speed development of
many kinds of NLP applications by taking care of low-level language
details not central to a given data problem or solution. It is now freely
available on the web to anyone wanting to process or pre-process text data.

The basic paradigm of PyElly is to rewrite natural language input into
some other text output, which might be SQL, XML, or some other form. This
falls short of full understanding, but can be quite helpful as a general
kind of preprocessing for data mining or for more precise indexing.

PyElly builds in flexible tokenization, syntax-driven parsing, English
inflectional and morphological stemming, macro substitutions, basic
and extended entity extraction, ambiguity handling, sentence recognition,
support for large external dictionaries, and a general procedural
framework for translating text from UTF-8 to UTF-8.

The latest version has been completely rewritten in mostly object-oriented
Python 2.7. It completed multiple stages of beta testing in 2014 and may
now be downloaded from GitHub at https://github.com/prohippo/pyelly.git .
The current release is v1.2.3.

To learn how to use PyElly, see the PyEllyManual.pdf file in the same
directory as this README.txt file. The manual has over a hundred pages of
information, including an overview of some basic linguistics. Documentation
of individual Python source files can be generated as needed with the
Python pydoc utility.

At present, PyElly consists of 63 Python modules comprising about fifteen
thousand lines of source code. There are also various definition files
to support basic various language processing capabilities in example
applications, including

* indexing - remove stopwords and get stems for content words from raw
             text input.
* texting  - readable text compression.
* doctor   - emulation of Weizenbaum's Doctor program.
* chinese  - basic translation of English to Chinese in simplified
             or traditional characters.
* querying - rewrite English questions as SQL queries for a Soviet
             military aircraft database.
* marking  - rewrite English text with XML markup
* name     - extract English personal names from text
* disambig - disambiguation of phrases with WordNet concept information.

These illustrate what you can do with PyElly and also serve as a basis for
comprehensive integration testing. Other applications will be added to the
PyElly package on GitHub in the future. You may use them as models for
building your own systems.

PyElly is intended mostly for educational use and is being released under
a BSD open-source license. Be advised that the current software and documentation
is still evolving, although the v1.1 release should be much more stable than
previous beta releases.

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
                      strengthen unit testing, add "querying" integration test
 0.4    -  04jul2014  support conceptual hierarchies in cognitive semantics
                      separate lookup tables for syntactic and semantic features
                      fix bugs in loading vocabulary tables from text input
                      fix bugs in loading conceptual hierarchies from text input
                      improve unit testing
                      add core of "disambig" application for integration testing
 0.4.1  -  13aug2014  clean up and flesh out "disambig" application
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
                      add "bad" application to test PyElly error reporting
 0.5.1  -  12sep2014  fix residual problems with error reporting and recovery
                      extend "bad" application for integration testing
 0.6    -  12oct2014  more input checking in vocabulary table compilation
                      more information in "disambig" application translations
                      better English inflectional and morphological stemming
                      English irregular stemming, update "echo" application
                      extend "chinese" application, better classifiers
 1.0    -  24dec2014  add comprehensive error reporting in inflectional stemming
                      add WordNet exceptions to cases handled by stemmers
                      upgrade pattern table matching and clean up code
                      fix bug in ellyWildcard with $ wildcard
                      update "querying" application
                      clean up various problems in "chinese" application
                      clean up all modules with PyLint
 1.0.1  -  01jan2015  bug fixes, cleanup ahead of v1.1
 1.0.2  -  12jan2015  bug fixes, cleanup and upgrade ahead of v1.1
                      clean up token extraction and lookup
 1.0.3  -  22jan2015  bug fixes, cleanup ahead of v1.1
                      upgrade code for token extraction and lookup
                      add first iteration of "marking" application
 1.0.4  -  26jan2015  bug fixes and upgrades ahead of v1.1
                      extend "marking" rules and integration test
 1.0.5  -  31jan2015  bug fixes, cleanup ahead of v1.1
                      better handling of punctuation in parsing
                      extend "marking" rules and integration test
 1.0.6  -  07feb2015  bug fixes, cleanup ahead of v1.1
                      improve unit testing
                      add "marking" rules and extend its integration test
 1.0.6a -  12feb2015  clean up code
                      make parsing with "marking" rules more efficient
                      update "marking" integration test
 1.1    -  21mar2015  add name recognition to entity extraction capability
                      add word phonetic signatures
                      add "name" integration test
                      minor cleanup of table loading source
                      fix bug in sentence recognition and clean
 1.2    -  03apr2015  replace Berkeley Database with SQLite
                      clean up PyElly initialization logic
 1.2.1  -  15apr2015  extend rules for "marking" application
                      extend "marking" integration test
                      more Unicode punctuation handling
                      fix input buffering for Unicode
                      fix morphological stemming problems
                      fix tokenization with new Unicode punctuation
                      fix macro table for new Unicode punctuation
                      add missing code for FIND in generative semantics
 1.2.2  -  01may2015  extend "test" amd "marking" integration tests
                      extend handling of punctuation
                      add phrase limit for avoiding runaway analysis
                      fix bug in warning of unused grammar symbols
                      fix bug in token lookup
                      improve morphological stemming
                      break out pickling as separate module
 1.2.3  -  08may2015  extend "marking" integration test
                      fix bug in numerical transformations with period
                      clean up rule definition diagnostics

New versions will reflect non-cosmetic changes in PyElly code. This typically
will require regeneration of any previously saved *.elly.bin files to ensure
correct operation. Changes only to PyElly sample application definition files,
unit testing input or key files, and PyElly documentation will be made from time
to time, but these will leave version numbers the same.

The PyElly website is at

    https://sites.google.com/site/pyellynaturallanguage/
