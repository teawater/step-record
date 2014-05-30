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
        self.add('Call command "%s" failed. ',
                 '调用命令"%s"失败。 ')
        self.add('Please install "%s" before go to next step.',
                 '在进行下一步以前请先安装软件包"%s"。')
        self.add('Input "y" and press "Enter" to continue',
                 '输入"y"后按回车键继续')
        self.add("Install packages failed.",
                 "安装包失败。")
        self.add('"%s" is not right.',
                 '"%s"不正确。')
        self.add('Current system is "%s".',
                 '当前系统是"%s".')
        self.add("Current system is not complete support.  Need execute some commands with yourself.\nIf you want KGTP support your system, please report to https://github.com/teawater/get-gdb/issues or teawater@gmail.com.",
                 "当前系统还没有被支持，需要手动执行一些命令。\n如果你希望KGTP支持你的系统，请汇报这个到 https://github.com/teawater/get-gdb/issues 或者 teawater@gmail.com。")
        self.add("Which version of GDB do you want to install?",
                 "你要安装哪个版本的GDB?")
        self.add("Build from source without check GDB in current system?",
                    "不检查当前系统，直接从源码编译GDB？")
        self.add('GDB in "%s" is OK for use.',
                    '在"%s"中的GDB可用。')
        self.add('GDB in software source is older than "%s".',
                    '软件源中的GDB比"%s"老。')
        self.add("Build and install GDB ...",
                    "编译和安装GDB...")
        self.add("Do you want to install GDB after it is built?",
                    "需要在编译GDB后安装它吗？")
        self.add("Please input the PREFIX directory that you want to install(GDB will be installed to PREFIX/bin/):",
                 "请输入安装的PREFIX目录（GDB将被安装在 PREFIX/bin/ 目录中）：")
        self.add("Please input the directory that you want to build GDB:",
                 '请输入编译GDB的目录：')
        self.add("Download GDB source package failed.",
                 '下载GDB源码包失败。')
        self.add("Uncompress GDB source package failed.",
                 '解压缩GDB源码包失败。')
        self.add("Config GDB failed.",
                 "配置GDB失败。")
        self.add("Build GDB failed.",
                 "编译GDB失败。")
        self.add("Install GDB failed.",
                 "安装GDB失败。")
        self.add('GDB %s is available in "%s".',
                 'GDB %s在"%s"。')
        self.add('"%s" exist.  Use it without download a new one?',
                 '"%s"存在，是否不下载而直接使用其？')

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
            return s
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
default_record_file = os.path.realpath("./step-record.log")
while True:
    record_file = raw_input(lang.string("Input the record file:[%s]" %default_record_file))
    if len(record_file) == 0:
        record_file = default_record_file
    record_file = os.path.realpath(record_file)
    if (os.path.exists(record_file)
        and not yes_no(lang.string('Overwrite "%s"?') %record_file, True, True)):
        continue
    try:
        record_fp = open(record_file, "w")
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
print(lang.string('Save log to "%s".') %record_file)