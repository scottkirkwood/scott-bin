#!/usr/bin/python
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""One-line documentation for pwgen module.

A detailed description of pwgen.
"""

__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import getpass
import math
import os
import random
import re
import sys

# From http://www.whatsmypass.com/the-top-500-worst-passwords-of-all-time
COMMON_PWD = [
 '123456', 'password', '12345678', '1234', 'pussy', '12345', 'dragon', 'qwerty',
 '696969', 'mustang', 'letmein', 'baseball', 'master', 'michael', 'football',
 'shadow', 'monkey', 'abc123', 'pass', 'fuckme', '6969', 'jordan', 'harley',
 'ranger', 'iwantu', 'jennifer', 'hunter', 'fuck', '2000', 'test', 'batman',
 'trustno1', 'thomas', 'tigger', 'robert', 'access', 'love', 'buster', '1234567',
 'soccer', 'hockey', 'killer', 'george', 'sexy', 'andrew', 'charlie', 'superman',
 'asshole', 'fuckyou', 'dallas', 'jessica', 'panties', 'pepper', '1111',
 'austin', 'william', 'daniel', 'golfer', 'summer', 'heather', 'hammer',
 'yankees', 'joshua', 'maggie', 'biteme', 'enter', 'ashley', 'thunder', 'cowboy',
 'silver', 'richard', 'fucker', 'orange', 'merlin', 'michelle', 'corvette',
 'bigdog', 'cheese', 'matthew', '121212', 'patrick', 'martin', 'freedom',
 'ginger', 'blowjob', 'nicole', 'sparky', 'yellow', 'camaro', 'secret', 'dick',
 'falcon', 'taylor', '111111', '131313', '123123', 'bitch', 'hello', 'scooter',
 'please', 'porsche', 'guitar', 'chelsea', 'black', 'diamond', 'nascar',
 'jackson', 'cameron', '654321', 'computer', 'amanda', 'wizard', 'xxxxxxxx',
 'money', 'phoenix', 'mickey', 'bailey', 'knight', 'iceman', 'tigers', 'purple',
 'andrea', 'horny', 'dakota', 'aaaaaa', 'player', 'sunshine', 'morgan',
 'starwars', 'boomer', 'cowboys', 'edward', 'charles', 'girls', 'booboo',
 'coffee', 'xxxxxx', 'bulldog', 'ncc1701', 'rabbit', 'peanut', 'john', 'johnny',
 'gandalf', 'spanky', 'winter', 'brandy', 'compaq', 'carlos', 'tennis', 'james',
 'mike', 'brandon', 'fender', 'anthony', 'blowme', 'ferrari', 'cookie',
 'chicken', 'maverick', 'chicago', 'joseph', 'diablo', 'sexsex', 'hardcore',
 '666666', 'willie', 'welcome', 'chris', 'panther', 'yamaha', 'justin', 'banana',
 'driver', 'marine', 'angels', 'fishing', 'david', 'maddog', 'hooters', 'wilson',
 'butthead', 'dennis', 'fucking', 'captain', 'bigdick', 'chester', 'smokey',
 'xavier', 'steven', 'viking', 'snoopy', 'blue', 'eagles', 'winner', 'samantha',
 'house', 'miller', 'flower', 'jack', 'firebird', 'butter', 'united', 'turtle',
 'steelers', 'tiffany', 'zxcvbn', 'tomcat', 'golf', 'bond007', 'bear', 'tiger',
 'doctor', 'gateway', 'gators', 'angel', 'junior', 'thx1138', 'porno', 'badboy',
 'debbie', 'spider', 'melissa', 'booger', '1212', 'flyers', 'fish', 'porn',
 'matrix', 'teens', 'scooby', 'jason', 'walter', 'cumshot', 'boston', 'braves',
 'yankee', 'lover', 'barney', 'victor', 'tucker', 'princess', 'mercedes', '5150',
 'doggie', 'zzzzzz', 'gunner', 'horney', 'bubba', '2112', 'fred', 'johnson',
 'xxxxx', 'tits', 'member', 'boobs', 'donald', 'bigdaddy', 'bronco', 'penis',
 'voyager', 'rangers', 'birdie', 'trouble', 'white', 'topgun', 'bigtits',
 'bitches', 'green', 'super', 'qazwsx', 'magic', 'lakers', 'rachel', 'slayer',
 'scott', '2222', 'asdf', 'video', 'london', '7777', 'marlboro', 'srinivas',
 'internet', 'action', 'carter', 'jasper', 'monster', 'teresa', 'jeremy',
 '11111111', 'bill', 'crystal', 'peter', 'pussies', 'cock', 'beer', 'rocket',
 'theman', 'oliver', 'prince', 'beach', 'amateur', '7777777', 'muffin', 'redsox',
 'star', 'testing', 'shannon', 'murphy', 'frank', 'hannah', 'dave', 'eagle1',
 '11111', 'mother', 'nathan', 'raiders', 'steve', 'forever', 'angela', 'viper',
 'ou812', 'jake', 'lovers', 'suckit', 'gregory', 'buddy', 'whatever', 'young',
 'nicholas', 'lucky', 'helpme', 'jackie', 'monica', 'midnight', 'college',
 'baby', 'cunt', 'brian', 'mark', 'startrek', 'sierra', 'leather', '232323',
 '4444', 'beavis', 'bigcock', 'happy', 'sophie', 'ladies', 'naughty', 'giants',
 'booty', 'blonde', 'fucked', 'golden', '0', 'fire', 'sandra', 'pookie',
 'packers', 'einstein', 'dolphins', 'chevy', 'winston', 'warrior', 'sammy',
 'slut', '8675309', 'zxcvbnm', 'nipples', 'power', 'victoria', 'asdfgh',
 'vagina', 'toyota', 'travis', 'hotdog', 'paris', 'rock', 'xxxx', 'extreme',
 'redskins', 'erotic', 'dirty', 'ford', 'freddy', 'arsenal', 'access14', 'wolf',
 'nipple', 'iloveyou', 'alex', 'florida', 'eric', 'legend', 'movie', 'success',
 'rosebud', 'jaguar', 'great', 'cool', 'cooper', '1313', 'scorpio', 'mountain',
 'madison', '987654', 'brazil', 'lauren', 'japan', 'naked', 'squirt', 'stars',
 'apple', 'alexis', 'aaaa', 'bonnie', 'peaches', 'jasmine', 'kevin', 'matt',
 'qwertyui', 'danielle', 'beaver', '4321', '4128', 'runner', 'swimming',
 'dolphin', 'gordon', 'casper', 'stupid', 'shit', 'saturn', 'gemini', 'apples',
 'august', '3333', 'canada', 'blazer', 'cumming', 'hunting', 'kitty', 'rainbow',
 '112233', 'arthur', 'cream', 'calvin', 'shaved', 'surfer', 'samson', 'kelly',
 'paul', 'mine', 'king', 'racing', '5555', 'eagle', 'hentai', 'newyork',
 'little', 'redwings', 'smith', 'sticky', 'cocacola', 'animal', 'broncos',
 'private', 'skippy', 'marvin', 'blondes', 'enjoy', 'girl', 'apollo', 'parker',
 'qwert', 'time', 'sydney', 'women', 'voodoo', 'magnum', 'juice', 'abgrtyu',
 '777777', 'dreams', 'maxwell', 'music', 'rush2112', 'russia', 'scorpion',
 'rebecca', 'tester', 'mistress', 'phantom', 'billy', '6666', 'albert' ]

# From http://en.wikipedia.org/wiki/Leet
# First list is sensible substitutions
# Second list are sub that I think are too hard to enter or too weird
LETTER_SUBSTITUTES = {
   'A': [
          ['4', '@', ],
          ['^', 'Z', 'aye', '/\\', '/-\\', ],
        ],
   'B': [
          ['6', 'l3', '|3', '|:', '/3', ')3'],
          ['P>', 'I3', '(3', '!3', ']3'],
        ],
   'C': [
          ['(', ],
          ['<', '{', ],
        ],
   'D': [
          ['|)', '[)',  ],
          ['cl', '|o', '])', 'I>', '|>', 'T)', '0', ],
        ],
   'E': [
          ['3', ],
          ['[-', '&', '|=-', ],
        ],
   'F': [
          [']=', '|='],
          ['ph', '}', '(=', 'I='],
        ],
   'G': [
          ['6', ],
          ['9', 'C-', 'gee', '(_-', 'cj', '&', '(_+', ],
        ],
   'H': [
          ['#', '}{',],
          ['/-/', ']-[', '|-|', '[-]', '}-{', ')-(', '(-)', ':-:',
           '|~|', ']~[', ],
        ],
   'I': [
          ['!', '1', '|', ':'],
          ['][', ']', 'eye', '3y3', ],
        ],
   'J': [
          [],
          ['_/', ']', '_|', '</', '(/'],
        ],
   'K': [
          ['|<', '|{',  ],
          ['|X',],
        ],
   'L': [
          ['1', '|', '|_', ],
          ['1_', 'lJ', ],
        ],
   'M': [
          ['^^', 'nn',],
          [ '|V|', ']v[', '//.', 'em', '(T)', '[V]', '(u)', '(v)', '(\\/)',
           '/|\\', '//\\\\//\\', '/|/|', '|\\/|', '/\\/\\', '/V\\', '[]\\/[]',
           '|^^|', '.\\\\', '/^^\\'],
        ],
   'N': [
          ['//', '/v', '~', '/\\/', '^/',  ],
          ['|\\|',  '[]', '[]\\[]', ']\\[', '//\\\\//', '[\\]', '<\\>',
           '{\\}', '[]\\'],
        ],
   'O': [
          ['0', '()'],
          ['[]', 'oh', 'p', ],
        ],
   'P': [
          ['9', 'q', '|o',],
          [ '|*', '|>', '|^(o)', '|"', '[]D', '|', '|7', ],
        ],
   'Q': [
          ['9', 'O,',  '()_', '0_' ],
          ['(_,)', '<|'],
        ],
   'R': [
          ['2', '12', '/2', '|^', '|2', 'l2', ],
          ['I2', '|2', '|~', 'lz', '[z', '|`'],
        ],
   'S': [
          ['$', '5', 'z'],
          ['ehs', 'es', ],
        ],
   'T': [
          ['+', '7',],
          [ '-|-', '1', '\'\][\''],
        ],
   'U': [
          [],
          ['M', '|_|', 'Y3W', 'L|'],
        ],
   'V': [
          ['\\/'],
          ['\\\\//'],
        ],
   'W': [
          ['vv', 'VV', 'UU',],
          ['\\/\\/', '\'//', '\\\\\'', '\\^/', '(n)', '\\V/', '\\X/',
           '\\|/', '\\_|_/', '\\\\//\\\\//', '\\_:_/', '(/\\)', ']I[', 'LL1'],
        ],
   'X': [
          ['%', '><',],
          [ '}{', 'ecks', '*', ')(', 'ex'],
        ],
   'Y': [
          ['-/', ],
          ['j', '`/', '`('],
        ],
   'Z': [
          ['%', '2'],
          ['7_', '~/_', '>_', ],
        ],
}

def EntropyPerSymbol(symbol_set_size):
  """Returns the entropy per symbol given symbol set size.
  >>> EntropyPerSymbol(10)  # 0-9
  3.3219280948873626
  >>> EntropyPerSymbol(26)  # a-z
  4.7004397181410926
  >>> EntropyPerSymbol(36)  # a-z, 0-9
  5.1699250014423122
  >>> EntropyPerSymbol(62)  # a-z, A-Z, 0-9
  5.9541963103868758
  >>> EntropyPerSymbol(94)  # keyboard characters
  6.5545888516776376
  """
  return math.log(symbol_set_size) / math.log(2.0)

def GuessDomainSize(pwd):
  """Returns a domain size.
  >>> GuessDomainSize('0123456789')
  10
  >>> GuessDomainSize('hellothere')
  26
  >>> GuessDomainSize('hello,there')
  31
  >>> GuessDomainSize('HelloThere')
  52
  >>> GuessDomainSize('Hello,there')
  57
  >>> GuessDomainSize('Hello1There')
  62
  >>> GuessDomainSize('Hell0,There')
  67
  >>> GuessDomainSize('@')
  94
  """
  if re.match(r'^[0-9]+$', pwd):
    return 10
  if re.match(r'^[0-9_/.,-]+$', pwd):
    return 15
  if re.match(r'^[a-z]+$', pwd):
    return 26
  if re.match(r'^[a-z_/.,-]+$', pwd):
    return 31
  if re.match(r'^[a-z0-9]+$', pwd):
    return 36
  if re.match(r'^[a-z0-9_/.,-]+$', pwd):
    return 41
  if re.match(r'^[a-zA-Z]+$', pwd):
    return 52
  if re.match(r'^[a-zA-Z_/.,-]+$', pwd):
    return 57
  if re.match(r'^[a-zA-Z0-9]+$', pwd):
    return 62
  if re.match(r'^[a-zA-Z0-9_/.,-]+$', pwd):
    return 67
  return 94

def GuessBitStrength(pwd):
  """Returns the bitstrength.
  >>> GuessBitStrength('0123')
  13
  >>> GuessBitStrength('09/39')
  20
  >>> GuessBitStrength('abcd')
  19
  >>> GuessBitStrength('ab09')
  21
  >>> GuessBitStrength('AbCd')
  23
  >>> GuessBitStrength('Ab09')
  24
  """
  bits =  EntropyPerSymbol(GuessDomainSize(pwd)) * len(pwd)
  return int(round(bits))

def TypingChar(ch):
  if re.search(r'[A-Z~!@#$%^&*()_+{}|:"<>?]', ch):
    return 2
  return 1

def TypingChars(pwd):
  """Returns number of keys pressed on keyboard.
  >>> TypingChars(r'xy')
  2
  >>> TypingChars(r'~!@#$%^&*()_+')
  14
  >>> TypingChars(r'`1234567890-=')
  13
  >>> TypingChars(r'{}|:"<>?')
  9
  >>> TypingChars(r"[]\;',./")
  8
  >>> TypingChars(r"aAaAaAaA")
  12
  """
  sum = 0
  last = 0
  for ch in pwd:
    c = TypingChar(ch)
    if c == 2 and last == 2:
      last = c
      c = 1
    else:
      last = c
    sum += c

  return sum

def PrintKeySummary(pwd, comment):
  print ' %-15r (%2d chars, %2d typing chars, %2d bits), %r' % (pwd,
      len(pwd), TypingChars(pwd), GuessBitStrength(pwd), comment)

def GetShortenedLower(line):
  re_first_ch = re.compile(r'\s([a-zA-Z0-9,/;])')
  chs = [line[0]]
  for match in re_first_ch.finditer(line):
    chs.append(match.group(1))
  chs = [ch.lower() for ch in chs]
  return ''.join(chs)


def RandomSubOneLeetLetter(ch):
  if ch in LETTER_SUBSTITUTES:
    subs = LETTER_SUBSTITUTES[ch][0]
  elif ch.upper() in LETTER_SUBSTITUTES:
    subs = LETTER_SUBSTITUTES[ch.upper()][0]
  else:
    return ch

  # returns's a random number with mean around log(size)
  # but with exponential decay (low numbers more common)
  exp = random.expovariate(1.0 / math.ceil(math.log(len(subs) + 1)))
  index = int(exp) % len(subs)
  return subs[index]

def GetLeet(line):
  ret = []
  for ch in list(line):
    if random.random() > 0.75:
      ret.append(RandomSubOneLeetLetter(ch))
    else:
      ret.append(ch)
  return ''.join(ret)


def GetShortenedManyCase(line):
  re_first_ch = re.compile(r'([\s?~:;,.-])([a-zA-Z0-9])?')
  chs = [line[0]]
  for match in re_first_ch.finditer(line):
    if match.group(2):
      chs.append(match.group(2))
    else:
      chs.append(match.group(1))
  chs = [ch for ch in chs]
  return ''.join(chs)


def PrintDefaultShort(line):
  PrintKeySummary(GetShortenedLower(line), line)

def PrintVariousShortened(line):
  PrintKeySummary(GetShortenedLower(line), line)
  PrintKeySummary(GetShortenedManyCase(line), line)
  PrintKeySummary(GetLeet(GetShortenedLower(line)), line)
  print

def AddOrInc(adict, word, inc=1):
  if word in adict:
    adict[word] += inc
  else:
    adict[word] = inc

def Blast(pwd):
  adict = {}
  AddOrInc(adict, GetShortenedLower(pwd), 1000)
  AddOrInc(adict, GetShortenedManyCase(pwd), 1000)
  for n in range(1000):
    sample = GetLeet(GetShortenedLower(pwd))
    AddOrInc(adict, sample)
  for n in range(1000):
    sample = GetLeet(GetShortenedManyCase(pwd))
    AddOrInc(adict, sample)

  ordered = []
  for a, freq in adict.items():
    ordered.append((freq, GuessBitStrength(a), TypingChars(a), a))
  ordered.sort()

  for freq, bits, typing, word in ordered:
    PrintKeySummary(word, pwd)

def Train(pwd):
  os.system('clear')
  print '%r' % pwd
  print 'Enter the password <enter> exists'
  while True:
    trial = getpass.getpass()
    if not trial:
      break
    if trial == pwd:
      print 'Correct'
    else:
      print 'Wrong'

def OpenPassword(fname):
  """Open file, also remove comments and blank lines."""
  stats = os.stat(fname)
  if stats[0] & 077:
    print 'File too permissive, should be:'
    print 'chmod 600 %s' % fname
    sys.exit(-1)

  lines = open(fname).read().split('\n')
  ret = []
  re_comment = re.compile(r'\s*#[^#]+$')
  for line in lines:
    line = re_comment.sub('', line).strip()
    if line:
      ret.append(line)
  return ret


def main(argv):
  import optparse
  parse = optparse.OptionParser()
  parse.add_option('-p', '--password', action='store_true', dest='ispwd',
      help='The password is there, not a phrase')
  parse.add_option('-t', '--train', action='store_true', dest='train',
      help='Practice one password')
  parse.add_option('-b', '--blast', action='store_true', dest='blast',
      help='Try lots of variations')
  parse.add_option('-v', '--variations', action='store_true', dest='variations',
      help='Try lots of variations')
  options, args = parse.parse_args()

  if len(args) == 0:
    print 'Usage: pass in a filename (must be chmod 600)'
    print 'example: pwgen.py ~/.ssh/pass'
    print '  Assume 1 line per password'
    print 'example: pwgen.py -t ~/.ssh/pass'
    print '  Assume 1st line is password, will train (practice) on it.'
    print 'example: pwgen.py -b ~/.ssh/pass'
    print '  Assume 1st line is password, will show l33t variations.'
    sys.exit(-1)

  fname = args[0]
  lines = OpenPassword(os.path.expanduser(fname))
  if options.train:
    if options.ispwd:
      Train(lines[0])
    else:
      Train(GetShortenedLower(lines[0]))
  elif options.ispwd:
    for line in lines:
      PrintKeySummary(line, line)
  elif options.blast:
    Blast(lines[0])
  elif options.variations:
    for line in lines:
      PrintVariousShortened(line)
  else:
    for line in lines:
      PrintVariousShortened(line)


if __name__ == '__main__':
  import doctest
  doctest.testmod()
  main(None)
