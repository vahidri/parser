# Compilers course
## Fall 2017

LL1 parser for a C-like language from scratch in Python3 :
See the code; it has nice comments and is legible

### Short Intro
+ Parser
    * Stack for detecting loops in the grammar
    * Upon wrong syntax in input code, prints the first error along with passed code part
    * Debug feature to see what's going under the hood
+ Scanner (Lexer)
    * Tokenizing the input using Special Tokens and Keywords
+ Engine
    * Reads the input grammar
    * Utilizes [Memoization](https://en.wikipedia.org/wiki/Memoization) to speed up generations
    * Generates Right Hand Side Table
    * Generates Parse Table (using First, Follow, and Predict functions)
    * In doing so checks if the grammar is LL1, if not prompts the faults

### Files used in the code:
* grammar file: "g.txt"
* special_tokens.txt
* keywords.txt

### In order to run the parser,

* place the test codes in "tests" directory (there are samples)
* run the 'run.sh'

