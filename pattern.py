import re
pattern = re.compile('[aA]nswer:[ ]*[0-9]+')
if pattern.match('answer: 123453'):
    print('Match!')
else:
    print('Not Match!')