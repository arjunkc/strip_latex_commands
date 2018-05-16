#!/usr/bin/python3
## License: MIT. Do whatever.
## Author: Arjun Krishnan
## Strips commands and environments from latex files.
## Usage
## strip_latex_commands.py filename
## Todo:
## 1. allow entry of specific environments from command line that overrides defaults.
## 1. does not allow spaces between arguments of commands like `\\opt`. Allows newlines though. To be fixed.
## 1. Dec 06 2016 Found an error. It seems to be deleting args twice. The del_args function should really only delete one matched parenthesis; i.e., one argument.
'''
Notes
Mar 28 2018 Appear to have fixed the problems with del_commands. It now stores delete locations, and then deletes together at the end. Also uses finditer, which is a bit faster.
Mar 27 2018 ~~Stuck on the code in del_commands which deletes a line. I'm assembling the final string from del locations.~~
Mar 27 2018 It gives me trouble when I have an \opt line inside an equation, and this does not remove the statement if it's by itself on that line. This causes latex errors when compiling. This is easily fixed manually, but really, this should fix it.
Mar 27 2018 Fixed the following problem: if you find \arjun before \arjunhl, then del_commands will find \arjun in \arjunhl first, and then it will struggle with finding the argument since it will try to find the argument starting at \arjun[h]l and fail to find a parens there. We could also make del_args smarter by making it crap out if it finds something other than a space, newline or open parens right after the command. I chose the easy route.
'''


import re
import sys

environs = ['note','longcalc','rambling','newnotes']
# list of [command, number of arguments]. For example `\opt{}{}` has 2 arguments. No spaces allowed between arguments.
commands = [[r'\\opt',2],[r'\\arjun',1],[r'\\jon',1],[r'\\notes',1],[r'\\arjunhl',1],[r'\\arjunnew',1],[r'\\jeremy',1],[r'\\optlongcalc',1]]
debug = True
interactive = False

# environments to strip
def del_args(s,nargs,start):
    # assumes s[start] = '{'
    pos=start
    parity=0
    cntargs = 0
    while cntargs < nargs and pos < len(s):
        if s[pos] == '}':
            parity = parity - 1
        elif s[pos] == '{':
            parity = parity + 1
        pos = pos + 1
        if parity == 0:
            cntargs = cntargs + 1
    try:
        if parity == 0:
            # if found matching parens at the end. 
            # overflow hack for pos=len(s) needed? does not seem to be necessary
            #s = s[0:start] + s[min(pos,len(s)-1):]
            return pos
        else:
            raise RuntimeError('mismatched parens')
    except RuntimeError:
        print('Error deleting arguments')

def del_environs(s,environs):
    for e in environs:
        str
        a = r'\\begin{' + e + r'}.*?\\end{' + e + '}'
        # the DOTALL flag catches newlines
        s = re.sub(a,'',s,flags=re.DOTALL)
    return s

def del_commands(s,commands):
    '''
    Delete commands of the form \arjunhl {hello}
    Does not handle nested commands correctly.
    To save newcommands, for example, it will ignore commands that are inside curly braces:
    { \command {} {} } will be ignored.
    '''
    del_locations = [0]
    for c in commands:
        # does lookahead for the command to see if of the form \command {
        matchstring = c[0] + r'\s*(?={)'
        matches = re.finditer(matchstring,s)

        for mat in matches:
            start = mat.start()
            end = mat.end()

            if debug:
                print("Start and end of match: ",(start,end))

            # delete arguments of command. pass start pos of '{' to del_args; returns new end
            # del_args(full string,number of arguments, position to start searching for arguments)
            end = del_args(s,c[1],end)


            # is it of the form { \command{}{} }? then ignore
            prev_brace = re.search('^[^}]*{',s[0:start][::-1])
            next_brace = re.search('^[^{]*}',s[end::])
            if prev_brace and next_brace:
                # ignore current match and ignore
                continue
            else:
                # is there empty space and a newline before the command? like in a \opt in an equation?
                # the -1 reverses the string, if I remember correctly
                empty_space_before = re.search('\s*\n',s[0:start][::-1])
                if empty_space_before and empty_space_before.start() == 0:
                    # if match found for empty space + newline before command start, then delete
                    start = start - empty_space_before.end()
                # delete the command too

                del_line = 'y'
                if interactive:
                    print('Command:\n', s[start:end])
                    del_line = input('Delete (Y/n)') or 'y'
                if del_line == 'y' or 'Y':
                    del_locations = del_locations + [start,end]
                
    del_locations.append(len(s)) #append length character to delete locations; it has even length
    # potential source of error if nested commands
    del_locations.sort()

    if debug:
        print('done finding matches')
        print('delete locations', del_locations)

    # reconstruct string
    del_string=''
    for x in range(0,len(del_locations),2):
        del_string = del_string + s[del_locations[x]:del_locations[x+1]] 
        #if debug:
            #print("substring: ",s[del_locations[x]:del_locations[x+1]])
            #print("del_string: ", del_string)

    return del_string 

if debug:
    print(sys.argv[0])

# reorder commands so longer commands are removed first. Ex: \arjunhl before \arjun
lenofcmd = lambda x: len(x[0])
commands.sort(key=lenofcmd,reverse=True)

if re.match(r'.*strip_latex_commands.py',sys.argv[0]):
    # if called externally. if sourced from ipython it won't run it
    infile = sys.argv[1]
    outfile = 'nocomments-' + infile

    # assuming we have at least one argument
    s = open(infile,'r').read()
    s = del_environs(s,environs)
    s = del_commands(s,commands)

    if debug:
        print("Writing file",outfile)

    f1 = open(outfile,'w')
    f1.write(s)

