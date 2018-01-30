PyElly is a rule-based natural language processing tool that has existed
for over forty years in various incarnations. It is now freely available
as open source software on the Web to anyone wanting to try it out. It is
written in version 2.7 of Python and employs SQLite for data management.

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
directory as this README.txt file. The manual has over a hundred fory pages
of information, including an overview of basic linguistics. Documentation
of individual Python source files can be generated as needed with the
Python pydoc utility from PyElly source files..

At present, PyElly consists of 64 Python modules comprising about ten
thousand lines of source code. There are also various definition files
to support basic various language processing capabilities. The PyElly
download includes rules for some example applications, including

* indexing - remove stopwords and get stems for content words from raw
             text input.
* texting  - readable text compression.
* doctor   - emulation of Weizenbaum's Doctor program.
* chinese  - basic translation of English to Chinese in simplified
             or traditional characters.
* querying - rewrite English questions as SQL queries for a Soviet
             military aircraft database.
* marking  - rewrite English text from the Web with shallow XML markup
* name     - extract mostly English personal names from text
* disambig - disambiguation of phrases with WordNet concept information.

These illustrate what you can do with PyElly and also serve as a basis for
comprehensive integration testing. Other applications will be added to the
PyElly package on GitHub in the future. You may use any of them as models for
building your own PyElly applications.

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
 1.3.4  -  07oct2015  improve morphological stemming
                      fix stemming bugs in vocabulary table lookup, clean code
                      extend various integration tests for stemming
                      improve output of ellySurvey
                      extend "marking" vocabulary
                      clean up "marking" integration test
                      change comment format in language definition files
 1.3.5  -  11nov2015  add control character for management of parse trees
                      filter out extra ASCII control chars from text input
                      clean up "marking" rules and integration test
                      fix minor bug in generative semantic compilation
                      better error reporting in cognitive semantic compilation
                      make FIND semantic command consistent with other operations
 1.3.5.1 - 26nov2015  fix bugs in control characters for parse tree management
                      clean up affected code modules
                      clean up "marking" rules and integration test
 1.3.5.2 - 15dec2015  fix bug in null check for cognitive semantics
                      rework control characters to be no longer punctuation
                      add rendering of contral characters in rule dumps
                      adjust "chinese" and "querying" integration test
                      adjust integration test script
                      extend "marking" rules with control characters
                      extend "marking" grammar and vocabulary
                      extend "marking" integration test
 1.3.6   - 01jan2016  fix bug in pattern matching of tokens
                      more flexible use of predefined syntactic features
                      extend "marking" language definition
                      extend "marking" integration testing
 1.3.6.1 - 08jan2016  fix bug integrating inflectional stemming and macros
                      clean up English inflectional stemming
                      extend and clean up suffix test cases
                      extend "echo" integration test
                      clean up and extend "marking" rules
                      extend "marking" integration test
 1.3.7   - 18feb2016  add token count to phrase data
                      check token position in cognitive semantics
                      check token count in cognitive semantics
                      allow more spaces in cognitive semantic clauses
                      clean up parse tree building
                      extend "marking" rules and integration test
                      extend, revise, correct cognitive semantic writeup
 1.3.8   - 25feb2016  extend token extraction for nonalphabetic additions
                      clean up basic character handling
                      extend "echo" integration test
                      update documentation
 1.3.9   - 03mar2016  fix various problems with checking of capitalization
                      clean up parse tree code
                      clean up documentation
                      extend "marking" rules and integration test
                      extend "echo" rules
 1.3.10  - 17mar2016  allow fractions to be handled as single tokens
                      extend "marking" rules and integration test
 1.3.11  - 13apr2016  allow vocabulary table entries to start with ','
                      extend "marking" rules and integration test
 1.3.12  - 23apr2016  more error checking in vocabulary table entries
                      extend "bad" rules to test error checking
                      extend "marking" rules and integration test
 1.3.13  - 04jul2016  better handling of hyphens
                      improve parse tree full dump
                      clean up documentation
 1.3.14  - 14jul2016  add method to turn off single feature bit
                      clean up handling of *L and *R syntactic features
                      fix capitalization bug in vocabulary lookup
                      recompile vocabulary only when needed
                      fix commentary bug with # at end of line
                      minor changes in reporting of table definition
                      clean up and extend documentation
 1.3.15  - 03aug2016  clean up procedure for recompiling language tables
                      clean up commentary and reporting
                      add basic cognitive semantics to pattern tables, entities
                      add feature inheritance checking
                      fix bug in disambiguation with type 0 rules
                      extend "test" integration testing for new patterns
                      extend "marking" application rules
                      clean up "doctor rules"
                      clean up and extend documentation
 1.3.16  - 21aug2016  add another recognizer for space chars
                      fix bug in pattern matching with spaces
                      extend "test" integration testing for space matching
                      clean up integration tests for space matching
                      update documentation
 1.3.17  - 07sep2016  fix bugs in handling tokenization breaks
                      define left enclosing punctuation in ellyChar
                      fix problems in ellyBase from changes in ellyChar.findBreak
                      fix ellyChar bug putting back left enclosing punctuation
                      implement alphabetic uppercase wildcard
                      clarify patternTable unit test
                      clarify macroTable unit test
                      extend "test" integration testing
                      clean up "marking" pattern and macro rules
                      clean up documentation
 1.3.18  - 16sep2016  fix integration problems in token lookup
                      improve unit testing for patternTable, substitutionBuffer
                      improve diagnostics for ellyBase, generativeProcedure
                      improve output representation of ellyBuffer, grammarRule
                      clean up "marking" rules and integration tests
                      extend "test" rules and integration test
                      clean up "doctor" and "chinese" rules
                      fix late setting of bias in leaf phrase nodes
 1.3.19  - 17oct1016  reorganize sentence extraction
                      fix problems with quotations and bracketed text
                      fix problems with English morphology rules
                      fix problem with ampersand in tokenization
                      fix problem with pattern matching on strings with brackets
                      fix problem with abbreviations and hyphenation
                      clean up and extend "marking" rules and integration tests
                      clean up documentation 
                      clean up ellyBase code and commentary
                      clean up ellySurvey code and fix dummy Tree class
                      fix problem with rule sequence numbers in parse tree dumping
                      use *x syntactic feature to identify period as punctuation
                      add check to avoid ord() error on ''
                      add missing error exit in loading vocabulary table
 1.3.20  - 01dec2016  clean up toplevel error checking and reporting
                      clean up logic for what rule files to recompile
                      fix problem with macro patterns ending in _ wildcard
                      add print statements for debugging
                      clean up PyElly table and tree dumps
                      extend "marking" rules and integration testing
 1.3.21  - 10dec2016  fix problem recognizing short bracketed tokens
                      clean up basic PyElly character handling
                      simplify output tags for "marking" example application
                      extend "marking" rules and integration testing
                      update and clarify documentation
 1.3.22  - 20dec2016  increase maximum syntactic category count to 72
                      add checks on semantic feature IDs in vocabulary rules
                      extend and clean up "marking" rules
                      extend "marking" integration testing
                      fix doTest script to make it self-complete
                      fix bug in *LEFT syntactic feature inheritance
                      fix bugs in date entity extraction
                      better checking of arguments for generative semantics
                      better error messages for cognitive semantic logic
                      fix bugs in stop punctuation exceptions
                      add nomatch logic for stop exceptions
                      update documentation
 1.3.23  - 03mar2017  increase maximum syntactic category count to 80
                      extend cases recognized by dateTransform
                      add more context to ellyCharInputStream logic
                      strengthen stopExceptions logic in nomatch()
                      update integration testing for new handling of dates
                      extend "marking" rules and integration test
                      update and clean up documentation
 1.3.24  - 15mar2017  fix bugs with buffer handling in generative semantics
                      add to cognitive semantic tracing output
                      show feature names sorted by index in grammar dump
                      clean up symbolTable error message
                      clean up commentary in parseTree
                      adjust debugging code in dateTransform
                      add extraction procedure for acronym definition
                      extend "marking" rules and integration test
                      update documentation
 1.4.0   - 20mar2017  enlarge Unicode subset recognized in input text
                      fix bugs and clean up ellyChar, add unit test
                      add vowels with diacriticals fo pinyin
                      special handling of CJK in ellyCharInputStream
                      update documentation
 1.4.1   - 26mar2017  improve encapsulation of ellyCharInputStream
                      add lookahead method for matching up brackets
                      extend and clean up unit test
                      rework ellySentenceReader logic for bracketed punctuation
                      extend and clean up "marking" rules and integration testing
                      improve unit testing support output
                      add consistency checking for semantic features
                      clean up source files along with line count of code
                      update documentation
 1.4.2   - 17apr2017  add char count check to cognitive semantics
                      add buffer alignment operation to generative semantics
                      extend "bad" rules to test error detection and recovery
                      fix omission in ellyBase handling of phrase token count
                      restore macroTable error check, normalize error messages
                      fix Unicode output redirection in multiple main modules
                      warn in symbolTable of syntactic types with similar names
                      add error checks in syntaxSpecification 
                      extend, reorganize, and clean up "marking" rules
                      extemd "marking" integration test
                      revise, correct, and update documentation
 1.4.3   - 26apr2017  add lowercase letter wildcard
                      simplify stopExceptions and default rules
                      note capitalization at start of current letter sequence
                      clean up commentary in various modules
                      extend "marking" rules
                      correct and update documentation
 1.4.4   - 04may2017  fix bugs with FAIL in generative semantics
                      fix bug with mergeBuffers() method in interpretiveContext
                      clean up translation failure reporting
                      add "fail" integration test with rules to PyElly suite
                      update documentation
 1.4.5   - 22may2017  fix bug in entity extraction when no phrase type is acceptable
                      fix bug with Unicode ellipsis in token extraction
                      add limited title recognition in entity extraction repertory
                      enhance output in unit testing support
                      extend "marking" rules and integration test
                      update documentation
 1.4.6   - 29may2017  make numbers with final decimal point as sentence stop exception
                      add lowercase letters as semiwildcards in PyElly pattern matches
                      correct bug in handling of right context in stopExceptions
                      change stopExceptions to make use of semiwildcard matching
                      clean up "default" stop exceptions
                      extend "marking" rules
                      update documentation
 1.4.7   - 04jun2017  fix capitalization bugs in generative semantics
                      clean up ellyChar methods and tables, extend unit test
                      add method to check patterns for wildcards not matching 1-to-1
                      add checking for patterns with only 1-to-1 wildcard marching
                      put in missing code for stopException matching of right context
                      clean up default stopException logic
                      update documentation, make more accurate
                      extend "marking" rules and integration test
 1.4.8   - 15jun2017  put in missing code for handling nonalphanumeric wildcard
                      allow space wildcard in optional pattern components
                      clean up macro substitution pattern matching
                      update documentation for wildcards
                      extend "marking" rules and integration test
 1.4.9   - 24jun2017  add Greek small letters to PyElly char set
                      extend "marking" rules and integration test
                      update and correct documentation
 1.4.10  -  4jul2017  add Unicode thin spaces to text recognized by PyElly
                      clean handling of various spaces in ellyChar
                      fix bug in matching patterns with space wildcards
                      fix ellyWild bug in deconverting pattern string
                      fix error detection in converting syntactic features
                      correct and extend stopException unit test
                      clean up debugging statements in PyElly modules
                      minor improvements in unit testing
                      extend "marking" rules and integration test
                      update documentation
 1.4.11  - 27jul2017  clean up and extend stop exception recognition
                      improve substitutionBuffer unit test
                      extend "marking" rules
                      update documentation
 1.4.12  - 01aug2017  more rational handling of _ in vocabulary table keys
                      add handling of superscript 1, 2, 3 as digits
                      make tokenization of Unicode consistent with input coding
                      improve vocabularyTable unit test
                      extend "marking" rules and integration test
                      update all integration tests for tokenization encoding
                      update and clean up documentation
 1.4.13  - 01sep2017  increase limit on syntactic types to 96
                      extend "marking" rules and integration test
                      update and clean up documentation
 1.4.14  - 14sep2017  correct bugs in compiling cognitive semantics
                      extend "marking" rules and integration test
                      update and clean up documentation
 1.4.15  - 20sep2017  fix bugs in stop exception recognition
                      clean up stop exception code, commentary, and debugging
                      improve stop exception unit testing
                      fix and clean up default stop exception rules
                      handle ellipsis in PyElly char input stream
                      add musical ♯ and ♭ to Elly character set
                      treat ° as embedded combining
                      extend "marking" rules and integration test
                      update documentation
 1.4.16  - 05oct2017  fix bugs in macro substitution
                      store macro rules as hashable objects
                      add angle brackets 〈〉 for PyElly delimiting
                      generalized handling for all bracketing in term lookup
                      improve algorithm for range of pattern matching
                      clean up and extend "marking" rules and integration test
                      update documenetation
 1.4.16.1  21oct2017  fix various bugs in dateTransform
                      extend "marking" rules
                      update documentation
 1.4.16.2  23nov2017  fix omissions in inflectional stemming logic
                      extend and correct "marking" rules
                      update documentation
 1.4.17  - 27nov2017  reimplement generative semantics FIND command
                      improve logic for recompiling PyElly tables
                      fix stemming problems with -n
                      fix punctuation problems with [ and ]
                      extend "marking" rules
                      update documentation
 1.4.18  - 31ded2017  rename vocabulary table building method to avoid conflict
                      improve handling of m dash in language definition rules
                      extend "marking" rules
                      update documentation
 1.4.18.1  01jan2018  clean up punctuation definitions
                      clean up and extend "marking" rules
                      update documentation
 1.4.19  - 06jan2018  add time period entity extraction
                      clean up and extend "marking" rules
                      update and revise documentation
 1.4.20  - 30jan2018  provide token list on parse tree overflow
                      clean up diagnostic output for parsing
                      fix bug in vocabulary table lookup of inflected entries
                      extend logic for -S inflections in English
                      extend "marking" rules
                      update and revise documentation

New versions will reflect non-cosmetic changes in PyElly code. This typically
will often require regenerating any previously saved *.elly.bin files to ensure
correct operation. Changes only to PyElly sample application definition files,
unit testing input or key files, and PyElly documentation will be made from time
to time, but these will leave version numbers the same, if they are the only
changes. Updates are still frequent; check for the latest files. The dates above
are for the initial release of a version, not the latest update,

The PyElly website is at

    https://sites.google.com/site/pyellynaturallanguage/
