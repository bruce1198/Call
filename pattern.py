import re
rule = '[aA]nswer:[ ]*[0-9]+'
while True:
    if pattern.match(input('string (pattern: '+rule+'): ')):
        print('Match!')
    else:
        print('Not Match!')