PyElly is a rule-based natural language processing tool that has existed
for over forty years in various incarnations.  It is now freely available
on the Web to anyone wanting to try it out.

PyElly is intended mainly for educational use, in that it allows a student
to engage natural language at a fine level of detail and learn the issues
involved in processing text data. It can be of interest to others, though,
because of its extensive support for handling the messy aspects of
language not central to most text data problems or their solutions.

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
Further development and refinement is ongoing.

To learn how to use PyElly, see the PyEllyManual.pdf file in the same
directory as this README.txt file. The manual has over a hundred pages of
information, including an overview of some basic linguistics. Documentation
of individual Python source files can be generated as needed with the
Python pydoc utility.

At present, PyElly consists of 64 Python modules comprising about sixteen
thousand lines of source code. There are also various definition files
to support basic various language processing capabilities. The PyElly
download also includes rules for some example applications, including

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

PyElly is free software released under a BSD open-source license for
educational and other uses. Be advised that the current software and
documentation is still evolving, although releases after v1.1 should be
more stable than preceding beta releases.

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
                      extend "chinese" application, improve classifiers
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
                      add more Unicode punctuation handling
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
 1.2.4  -  15may2015  extend "marking" integration test
                      fix bug in scoring plausibility of phrases
                      fix simplified character translation in "chinese" test
                      add tracing to cognitive semantic logic
                      better checking on feature set identifiers
 1.2.5  -  25may2015  clean up "marking" rules and integration test
                      improve input code for syntactic and semantic features
                      increase upper limit on phrase count
                      fix bugs in parse tree growth restrictions
                      fix bug in inheriting syntactic features with *L, *R
                      change directions of FIND command to be more consistent
                      update "test" and "bad" grammars for PyElly changes
                      raise exception for  phrase overflows
 1.2.6  -  01jun2015  clean up "marking" application rules
                      extend "marking" integration test
                      clean up logic for loading grammar and vocabulary
                      improve cognitive semantic tracing
                      add diagnostic output for parsing
 1.2.7  -  08jun2015  clean up "marking" rules and change integration test key
                      fix bug in morphological analysis match conditions
                      make punctuation syntax feature ID consistent
                      add automatic check for consistency of all feature IDs
                      fill out description of MERGE command in User's Manual
 1.2.8  -  15jun2015  better debugging for reading in sentences to process
                      fix incorrect stop exception
                      fix inconsistent feature ID in "chinese" grammar
                      fix problem in parse tree dump with big phrase IDs
                      fix bug with apostrophe as quotation mark
                      clean up "marking" application rules
 1.2.9  -  22jun2015  clean up "marking" application rules
                      fix swapping bug in reordering of ambiguous phrases
                      improve diagnostic output
 1.2.10 -  29jun2015  clean up and extend "marking" application
                      fix formatting problem in SHOW semantic command
                      clean up output for TRACE and SHOW
                      add VIEW instrumentation command
                      minor improvements in test scripts and data
 1.2.11 -  06jul2015  fix bug in computing plausibility scores for parses
                      improve reporting of rule usage in parse tree dump
                      clean up "marking" application rules
                      extend "marking" integration test
                      fix bug in handling forms of ellipsis
 1.2.12 -  13jul2015  fix bug in converting ellyBase parse tree depth arg
                      fix bug in adjusting grammar rule biases
                      clean up diagnostic output
                      extend "marking" integration test
 1.2.13 -  20jul2015  fix swapping bug in reordering of ambiguous phrases
                      define Kernel class to make phrase swapping cleaner
                      add check for multiple definition of subprocedures
                      extend "marking" integration test
                      improve default suffix removal
 1.2.14 -  30jul2015  fix minor bug in display of rules invoked for parse tree
                      fix problems in punctuation recognition, clean up code
                      fix bug in handling ` as punctuation in token extraction
                      extend "marking" application rules
 1.2.15 -  03aug2015  fix problems in tracking capitalization, clean up code
                      improve diagnostic output
                      extend "marking" integration test
 1.2.16 -  21aug2015  fix bug in pattern table method
                      improve default suffix removal
                      improve cognitive semantic diagnostics
                      add handling of em and en dashes in tokentization
                      extend default punctuation handling
                      extend "marking" rules and integration test
 1.3    -  06sep2015  add reset of inherited syntactic and semantic features
                      fix bugs in handling features and clean up code
 1.3.1  -  13sep2015  make integration testing script more flexible
                      extend basic "test" integration test
                      clean up "marking" integration test
                      fix missing cognitive semantics for leaf phrase nodes
                      improve diagnostic output
 1.3.2  -  23sep2015  add ellySurvey tool for vocabulary development
                      fix text normalization bug in handling input
                      add apostrophe wildcard
                      fix bugs in binding to text matching wildcards
                      clean up token lookup
                      clean up "marking" rules
 1.3.3  -  03oct2015  fix bugs in vocabulary lookup and tokenization
                      clean up vocabulary development tool
                      clean up char and wildcard definitions
                      improve release checking for binary tables
                      improve diagnostic output
                      extend "echo", "marking" rules and integration test
                      add "stem" application rules and integration test

New versions will reflect non-cosmetic changes in PyElly code. This typically
will require regeneration of any previously saved *.elly.bin files to ensure
correct operation. Changes only to PyElly sample application definition files,
unit testing input or key files, and PyElly documentation will be made from time
to time, but these will leave version numbers the same.

The PyElly website is at

    https://sites.google.com/site/pyellynaturallanguage/
