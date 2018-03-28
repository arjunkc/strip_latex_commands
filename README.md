# Introduction

This script strip latex commands and enviroments. It works in python3, and has no external dependencies.

I use it to strip notes and other optional environments from my latex file before I post it to the arxiv.

Usage:
```    
    strip_latex_commands.py filename.tex
```

Output:

A file called `nocomments-filename.tex`.

Its current controlled entirely by internal variables. The relevant ones are

1.  debug = True or False. Spits out a bunch 
1.  interactive = True or False. Asks before removing environments or commands.
1.  commands. A python list of commands to strip, of the form `['\\emph','\\arjun']` and so on.
1.  environments. A list of environments of the form `['note',...]`. 

Eventually, I will add command line options to control it instead. The command list and environment list should be overridable using a config file in the current directory.

# Know bugs

It will remove commands from inside \newcommand environments if filename.tex contains them. For example, if 

    commands = ['\\arjun']

and filename.tex contains

    \newcommand{\arjun}[1]{\emph{#1}}

Then nocomments-filename.tex will contain

    \newcommand{}

This will cause an error. I manually edit nocomments-filename.tex to remove this now. I will eventually fix this.




