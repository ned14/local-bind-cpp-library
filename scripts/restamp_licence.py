#!/usr/bin/python
# Restamps the top of a source file with licence boilerplate
# (C) 2017 Niall Douglas http://www.nedproductions.biz/
# File created: Apr 2017
#
# Todo:
#  - Support for .py, .cmake, CMakeLists.txt
#  - Copyright needs to be auto generated:
# (C) xxxx-thisyear Niall Douglas URL (>= x commits), ...
#  - Additional names come from git shortlog -sn <path>
#    - Niall Douglas (s [underscore] sourceforge {at} nedprod [dot] com) => Niall Douglas
#    - ned Productions Jenkins build bot => Niall Douglas
#    - Jenkins nedprod CI => Niall Douglas
#    - Niall Douglas (s [underscore] sourceforge {at} nedprod [dot] com => Niall Douglas

from __future__ import print_function

import os, sys, re, datetime, subprocess

path = sys.argv[1] if len(sys.argv)>1 else '.'
extensions = ['.cpp', '.hpp', '.ipp', '.c', '.h']

licence = '''Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License in the accompanying file
Licence.txt or at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Distributed under the Boost Software License, Version 1.0.
    (See accompanying file Licence.txt or copy at
          http://www.boost.org/LICENSE_1_0.txt)
'''

replace = [ licence,
'''Boost Software License - Version 1.0 - August 17th, 2003

Permission is hereby granted, free of charge, to any person or organization
obtaining a copy of the software and accompanying documentation covered by
this license (the "Software") to use, reproduce, display, distribute,
execute, and transmit the Software, and to prepare derivative works of the
Software, and to permit third-parties to whom the Software is furnished to
do so, all subject to the following:

The copyright notices in the Software and this entire statement, including
the above license grant, this restriction and the following disclaimer,
must be included in all copies of the Software, in whole or in part, and
all derivative works of the Software, unless such copies or derivative
works are solely in the form of machine-executable object code generated by
a source language processor.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''
]


# Most of my code has the following header:
# /* bitfield.hpp
# Yet another C++ 11 constexpr bitfield
# (C) 2016 Niall Douglas http://www.nedprod.com/
# File Created: Aug 2016
#
#
# Boost Software License - Version 1.0 - August 17th, 2003
# ...
# */
#
# Some code omits the licence, but has some custom notes you'd want to preserve
# Newer code omts the file name at the top
# Really old code stops just before the "File Created:"

class SourceFile(object):
    todayyear = datetime.datetime.now().year
    niallstrings = [ 'Niall Douglas', 'ned Productions Jenkins build bot', 'Jenkins nedprod CI' ]
    
    def __init__(self):
        self.title = None
        self.description = None
        self.startyear = 0
        self.endyear = None
        self.copyright = None
        self.created = None
        self.remainder = None
        self.matchedlen = 0
        self.history = []

    def refresh_history(self, path):
        path = path.replace('\\', '/')
        # git shortlog hangs if called with a stdin which is not a TTY, so hack the problem
        if sys.platform == 'win32':
            historyre = subprocess.check_output(['git', 'shortlog', '-sne', '--', path, '<', 'CON'], shell = True)
        else:
            historyre = subprocess.check_output(['git', 'shortlog', '-sne', '--', path, '<', '/dev/tty'], shell = True)
        # Format will be:
        #    203  Niall Douglas (s [underscore] sourceforge {at} nedprod [dot] com) <spamtrap@nedprod.com>
        historyre = historyre.split('\n')
        history_ = []
        for line in historyre:
            line = line.rstrip()
            if line:
                result = re.match(r'\s*(\d+)\s+(.+) <(.+)>', line)
                assert result
                history_.append((int(result.group(1)), result.group(2), result.group(3)))
        # Accumulate all Niall Douglas commits
        niallcommits = 0
        self.history = []
        for item in history_:
            for niall in self.niallstrings:
                if niall in item[1]:
                    niallcommits += item[0]
                    break
            else:
                self.history.append(item)
        self.history.append((niallcommits, 'Niall Douglas', 'http://www.nedproductions.biz/'))
        self.history.sort(reverse = True)


class CppSourceFile(SourceFile):
    def match_header(self, contents):
        """Match a comment header at the top of my C++ source files and extract stuff,
        returning False if failed to match"""
        result = re.match(r'/\* ([^\n]+)\n([^\n]+)\n\(C\) (\d\d\d\d)(-\d\d\d\d)? (Niall Douglas[^\n]+)\n([^\n*/]+)?(.*?\*/)', contents, flags = re.DOTALL)
        if not result:
            result = re.match(r'()/\* ([^\n]+)\n\(C\) (\d\d\d\d)(-\d\d\d\d)? (Niall Douglas[^\n]+)\n([^\n*/]+)?(.*?\*/)', contents, flags = re.DOTALL)
        if not result:
            return False
        self.title = result.group(1).lstrip().rstrip()
        self.description = result.group(2).lstrip().rstrip()
        self.startyear = int(result.group(3))
        self.endyear = result.group(4)
        if self.endyear is not None:
            self.endyear = int(self.endyear[1:])
        self.copyright = result.group(5).lstrip().rstrip()
        self.created = result.group(6)
        if self.created is not None:
            self.created = self.created.lstrip().rstrip()
        self.remainder = result.group(7).lstrip().rstrip()
        self.matchedlen = len(result.group(0))
        return True

    def gen_header(self):
        """Returns a regenerated header for C++ source"""
        ret = '/* ' + self.description + '\n(C) ' + str(self.startyear)
        if self.todayyear != self.startyear:
            ret += '-' + str(self.todayyear)
        ret += ' '
        for idx in range(0, len(self.history)):
            ret += self.history[idx][1] + ' <' + self.history[idx][2] + '> (' + str(self.history[idx][0])
            ret += ' commit)' if self.history[idx][0] == 1 else ' commits)'
            if idx == len(self.history) - 2:
                ret += ' and '
            elif idx < len(self.history) - 2:
                ret += ', '
        ret += '\n'
        if self.created:
            ret += self.created + '\n'
        ret += '\n\n'
        ret += licence
        if self.remainder != '*/':
            ret += '\n\n'
        ret += self.remainder
        return ret

for dirpath, dirnames, filenames in os.walk(path):
    for filename in filenames:
        process = False
        for ext in extensions:
            if filename[-len(ext):] == ext:
                process = True
                break
        if not process:
            continue
        path = os.path.join(dirpath, filename)
        if '.git' not in path:
            with open(path, 'rt') as ih:
                contents = ih.read()
            processor = CppSourceFile()
            if not processor.match_header(contents):
                print("NOTE: Did not match", path)
            else:
                # Remove any licence boilerplates from the header comment
                for r in replace:
                    idx = processor.remainder.find(r)
                    if idx != -1:
                        processor.remainder = processor.remainder[:idx] + processor.remainder[idx+len(r):]
                        processor.remainder = processor.remainder.lstrip()
                #print("\n\nMatched", path, "with:\n  title=", processor.title, "\n  description=", processor.description,
                #      "\n  startyear=", processor.startyear, "\n  endyear=", processor.endyear, "\n  copyright=", processor.copyright,
                #      "\n  created=", processor.created, "\n  remainder=", processor.remainder)
                processor.refresh_history(path)
                replacement = processor.gen_header()
                #print("\n\nMatched", path, "with:\n\n" + replacement)
                contents2 = replacement + contents[processor.matchedlen:]
                if contents != contents2:
                    with open(path, 'wt') as oh:
                        oh.write(contents2)
                    print("Updated", path)
                else:
                    print("No need to update", path)
                    
        