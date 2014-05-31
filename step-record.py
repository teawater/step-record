#!/usr/bin/python
# -*- coding: utf-8 -*-

import gdb
import os, re

class Lang(object):
    '''Language class.'''
    def __init__(self, language="en"):
        self.data = {}
        self.language = language
        self.is_set = False
        self.add("Input the record file:[%s]",
                 "记录文件名:[%s]")
        self.add('Overwrite "%s"?',
                 '覆盖“%s”？')
        self.add("Which step command do you want to use?",
                 "你要使用哪个单步命令？")
        self.add("Please input the number of breakpoint that will stop the record(0 means every breakpoint):[0]",
                 "请输入停止记录的断点号（0代表所有断点）:[0]")
        self.add("Record the duplicate log?",
                 "记录重复的日志？")
        self.add("Record the function name?",
                 "记录函数名？")
        self.add("Record the file name?",
                 "记录文件名？")
        self.add("Record the number of line?",
                 "记录文件行？")
        self.add('Saved log to "%s".',
                 '记录保存到“%s”。')

    def set_language(self, language):
        if language != "":
            if language[0] == "c" or language[0] == "C":
                self.language = "cn"
            else:
                self.language = "en"
            self.is_set = True

    def add(self, en, cn):
        self.data[en] = cn

    def string(self, s):
        if self.language == "en" or (not self.data.has_key(s)):
            print self.language
        return self.data[s]

def select_from_list(entry_list, default_entry, introduction):
    if type(entry_list) == dict:
        entry_dict = entry_list
        entry_list = list(entry_dict.keys())
        entry_is_dict = True
    else:
        entry_is_dict = False
    while True:
        default = -1
        default_str = ""
        for i in range(0, len(entry_list)):
            if entry_is_dict:
                print("[%d] %s %s" %(i, entry_list[i], entry_dict[entry_list[i]]))
            else:
                print("[%d] %s" %(i, entry_list[i]))
            if default_entry != "" and entry_list[i] == default_entry:
                default = i
                default_str = "[%d]" %i
        try:
            select = input(introduction + default_str)
        except SyntaxError:
            select = default
        except Exception:
            select = -1
        if select >= 0 and select < len(entry_list):
            break
    return entry_list[select]

def yes_no(string="", has_default=False, default_answer=True):
    if has_default:
        if default_answer:
            default_str = " [Yes]/No:"
        else:
            default_str = " Yes/[No]:"
    else:
        default_str = " Yes/No:"
    while True:
        s = raw_input(string + default_str)
        if len(s) == 0:
            if has_default:
                return default_answer
            continue
        if s[0] == "n" or s[0] == "N":
            return False
        if s[0] == "y" or s[0] == "Y":
            return True

lang = Lang()
lang.set_language(select_from_list(("English", "Chinese"), "", "Which language do you want to use?"))

#Got record_fp
default_record_file_name = os.path.realpath("./step-record.log")
while True:
    record_file_name = raw_input(lang.string("Input the record file:[%s]") %default_record_file_name)
    if len(record_file_name) == 0:
        record_file_name = default_record_file_name
    record_file_name = os.path.realpath(record_file_name)
    if (os.path.exists(record_file_name)
        and not yes_no(lang.string('Overwrite "%s"?') %record_file_name, True, True)):
        continue
    try:
        record_fp = open(record_file_name, "w")
    except:
        continue
    break

#Get step_cmd
step_cmd = select_from_list(("step", "stepi", "next", "nexti"), "step", lang.string("Which step command do you want to use?"))

#Get break_num
while True:
    break_num = raw_input(lang.string("Please input the number of breakpoint that will stop the record(0 means every breakpoint):[0]"))
    try:
        s = gdb.execute("info breakpoints " + break_num, True, True)
    except:
        continue
    if s[:13] != "No breakpoint":
        break
break_num = "Breakpoint " + break_num

#Get record_duplicate
record_duplicate = yes_no(lang.string("Record the duplicate log?"), True, False)

#Get record_function
record_function = yes_no(lang.string("Record the function name?"), True, True)

#Get record_file
record_file = yes_no(lang.string("Record the file name?"), True, True)

#Get record_line
record_line = yes_no(lang.string("Record the number of line?"), True, True)

prev_line = ""
while True:
    try:
        s = gdb.execute(step_cmd, True, True)
        s = s.lstrip()

        l = gdb.execute("info line", True, True)
        l = re.match(r'Line (\d+) of "(.*)".*<([^+]*).*>', l)
        if not bool(l):
            break
        line = ""
        if record_function:
            line += l.group(3)
        if record_file:
            if len(line) > 0:
                line += " "
            line += l.group(2)
        if record_line:
            if len(line) > 0:
                line += " "
            line += l.group(1)
        line += "\n"
        if not record_duplicate and line != prev_line:
            record_fp.write(line)
            prev_line = line

        if len(s) >= len(break_num) and s[:len(break_num)] == break_num:
            break
    except Exception, x:
        print x
        break

record_fp.close()
print(lang.string('Saved log to "%s".') %record_file_name)
