#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : cmd_template.py
@Time    : 2022/09/25 21:45:48
@Author  : Roderick Chan
@Email   : roderickchan@foxmail.com
@Desc    : subcommand template
'''


import os
import shutil
import subprocess
import sys
from datetime import datetime

import click
from pwn import wget, which

from pwncli.cli import pass_environ

from ..utils.decorates import limit_calls
from ..utils.misc import one_gadget


def _find_libc_in_directory(directory):
    """Recursively find libc file in the given directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith("libc.so") or file.startswith("libc-2."):
                full_path = os.path.join(root, file)
                with open(full_path, "rb") as f:
                    data = f.read(4)
                    if data == b"\x7fELF":
                        return full_path
    return None


def _find_elf_and_libc_in_directory(directory):
    """Recursively find ELF and libc files in the given directory."""
    libc_file = ""
    elf_file = ""
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if not os.path.isfile(full_path):
                continue
            with open(full_path, "rb") as f:
                data = f.read(4)
                if data != b"\x7fELF":
                    continue
                if file.startswith("libc.so") or file.startswith("libc-2."):
                    libc_file = full_path
                elif file.startswith("ld.so") or file.startswith("ld-2."):
                    pass
                else:
                    if not elf_file:
                        elf_file = full_path
    return elf_file, libc_file


def generate_cli_exp(ctx, directory):
    content = """#!/usr/bin/env python3
# Date: {}
# Link: https://github.com/RoderickChan/pwncli
# Usage:
#     Debug : python3 exp.py debug elf-file-path -t -b malloc
#     Remote: python3 exp.py remote elf-file-path ip:port

from pwncli import *
cli_script()
{}

io: tube = gift.io
elf: ELF = gift.elf
libc: ELF = gift.libc

# one_gadgets: list = get_current_one_gadget_from_libc(more=False)
# CurrentGadgets.set_find_area(find_in_elf=True, find_in_libc=False, do_initial=False)

def cmd(i, prompt):
    sla(prompt, i)

def add():
    cmd('1')
    #......

def edit():
    cmd('2')
    #......

def show():
    cmd('3')
    #......

def dele():
    cmd('4')
    #......


ia()
"""
    exp_path = os.path.join(directory, "exp_cli.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            sys.exit(0)

    set_remote_file = _find_libc_in_directory(directory)
    if set_remote_file:
        if set_remote_file.startswith(directory):
            set_remote_file = os.path.relpath(set_remote_file, directory)
        add_remote = "set_remote_libc('{}')".format(set_remote_file)
    else:
        add_remote = ""

    content = content.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), add_remote)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate cli mode exp file: {}".format(exp_path))


def generate_lib_exp(ctx, directory):
    content = """#!/usr/bin/env python3
# Date: {}
# Link: https://github.com/RoderickChan/pwncli

from pwncli import *

{}
context.binary = '{}'
context.log_level = 'debug'
context.timeout = 5

gift.io = process('{}')
# gift.io = remote('127.0.0.1', 13337)
gift.elf = ELF('{}')
gift.libc = ELF('{}')

io: tube = gift.io
elf: ELF = gift.elf
libc: ELF = gift.libc

# one_gadgets: list = get_current_one_gadget_from_libc(more=False)
# CurrentGadgets.set_find_area(find_in_elf=True, find_in_libc=False, do_initial=False)

def debug(gdbscript="", stop=False):
    if isinstance(io, process):
        gdb.attach(io, gdbscript=gdbscript)
        if stop:
            pause()

def cmd(i, prompt):
    sla(prompt, i)

def add():
    cmd('1')
    #......

def edit():
    cmd('2')
    #......

def show():
    cmd('3')
    #......

def dele():
    cmd('4')
    #......


ia()
"""
    exp_path = os.path.join(directory, "exp_lib.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            sys.exit(0)

    elf_file, libc_file = _find_elf_and_libc_in_directory(directory)


    terminal = "context.terminal = "
    if which("tmux"):
        terminal += "['tmux', 'splitw', '-h']"
    elif which('gnome-terminal'):
        terminal += "['tmux', '--', 'sh', '-c']"
    else:
        terminal = ""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = content.format(current_time, terminal, elf_file, elf_file, elf_file, libc_file)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate lib mode exp file: {}".format(exp_path))


def generate_pwn_exp(ctx, directory):
    content = """#!/usr/bin/env python3

from pwn import *
from pwncli import *


ELF_FILE = "{}"
REMOTE = b"127.0.0.1:1234"
DI, PORT = REMOTE.split(b":")
PORT = int(PORT)

{}
context.binary = ELF_FILE
context.log_level = 'debug'
context.timeout = 5

io = process([ELF_FILE])
# io = remote(DI, PORT)
elf = ELF(ELF_FILE)
libc = ELF('{}')
{}

def debug(gdbscript="", stop=False):
    if isinstance(io, process):
        gdb.attach(io, gdbscript=gdbscript)
        if stop:
            pause()

leak = lambda name, address: log.info(
    "\033[1;36m{{}}\033[0m ===> \033[1;33m{{}}\033[0m".format(name, hex(address))
)
uu64 = lambda recvlen: u64(r(recvlen).ljust(8, b"\\x00"))
s   = io.send
sl  = io.sendline
sla = io.sendlineafter
sa  = io.sendafter
r   = io.recv
ru  = io.recvuntil
rl  = io.recvline
ia  = io.interactive
ic  = io.close


ia()
"""
    exp_path = os.path.join(directory, "exp_pwn.py")
    if os.path.exists(exp_path):
        res = input("[*] {} exists, continue to overwrite? [y/n] ".format(exp_path))
        if res.lower().strip() != "y":
            ctx.vlog("template-command --> Stop creating the file: {}".format(exp_path))
            sys.exit(0)

    elf_file, libc_file = _find_elf_and_libc_in_directory(directory)


    terminal = "context.terminal = "
    if which("tmux"):
        terminal += "['tmux', 'splitw', '-h']"
    elif which('gnome-terminal'):
        terminal += "['tmux', '--', 'sh', '-c']"
    else:
        terminal = ""
    
    #current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    onegagets = ""
    if libc_file and which("one_gadget"):
        _og = one_gadget(libc_file, more=False)
        _og = "[" + ", ".join([hex(x) for x in _og]) + "]"
        onegagets = "one_gadgets = " + _og
    content = content.format(elf_file, terminal, libc_file, onegagets)
    with open(exp_path, "wt", encoding="utf-8") as f:
        f.write(content)
    
    subprocess.run(["chmod", "+x", exp_path])
    ctx.vlog("template-command --> Generate pwn exp file: {}".format(exp_path))


def _prepare_files_for_kernel_exp(ctx, ko_name, run_sh, cpio_prefix, need_gzip):
    url = "https://raw.githubusercontent.com/RoderickChan/CVE-ANALYZE/main/pwn.h"
    try:
        wget(url, save=True, timeout=300)
        ctx.vlog("template-command --> Download pwn.h success!")
    except:
        ctx.verrlog("template-command --> Cannot download {}".format(url))

    url = "https://raw.githubusercontent.com/RoderickChan/CVE-ANALYZE/main/exp.py"
    try:
        wget(url, save=True, timeout=300)
        ctx.vlog("template-command --> Download exp.py success!")
    except:
        ctx.verrlog("template-command --> Cannot download {}".format(url))

    with open("debug-gef.sh", "wt") as fp:
        ctx.vlog("template-command --> Generate debug-gef.sh.")
        fp.write("""#!/bin/bash
                 
gdb-multiarch ./vmlinux \\
    -ex "gef-remote --qemu-user 127.0.0.1 1234" \\
    -ex "add-symbol-file ./vmlinux 0xffffffff81000000" \\
    -ex "add-symbol-file ./{} 0xffffffffc0002000"
""".format(ko_name))

    with open("debug-pwndbg.sh", "wt") as fp:
        ctx.vlog("template-command --> Generate debug-pwndbg.sh.")
        fp.write("""#!/bin/bash
                 
gdb-multiarch ./vmlinux \\
    -ex "target remote 127.0.0.1:1234" \\
    -ex "add-symbol-file ./vmlinux 0xffffffff81000000" \\
    -ex "add-symbol-file ./{} 0xffffffffc0002000"
""".format(ko_name))
    
    os.chmod("debug-gef.sh", 0o755)
    os.chmod("debug-pwndbg.sh", 0o755)
    
    if cpio_prefix:
        ctx.vlog("template-command --> Do cpio operations.")
        os.makedirs(cpio_prefix, exist_ok=True)
        if need_gzip:
            os.rename(cpio_prefix + ".cpio.gz", "./{}/{}.cpio.gz".format(cpio_prefix, cpio_prefix))
        else:
            os.rename(cpio_prefix + ".cpio", "./{}/{}.cpio".format(cpio_prefix, cpio_prefix))
        cmd = "cd ./{}".format(cpio_prefix)
        if need_gzip:
            cmd += " && gzip -d {}.cpio.gz".format(cpio_prefix)
        cmd += " && cpio -idm < {}.cpio".format(cpio_prefix)
        
        os.system(cmd)
        os.unlink("./{}/{}.cpio".format(cpio_prefix, cpio_prefix))
        
    if run_sh:
        ctx.vlog("template-command --> Rewrite {}.".format(run_sh))
        newcontent = ""
        with open(run_sh, "rt", encoding="utf-8") as fp:
            skip_firstline = 0
            for line in fp:
                if line.startswith("#"):
                    if skip_firstline == 0:
                        skip_firstline = 1
                        line += "set -ex\n"
                        line += "/bin/rm -rf ./{}/exp*\n".format(cpio_prefix)
                        line += "gcc -o ./{}/exp exp.c -w -static -O0 -lpthread\n".format(cpio_prefix)
                        line += "# musl-gcc -o ./{}/exp exp.c -w -static -O0 -lpthread -idirafter /usr/include/ -idirafter /usr/include/x86_64-linux-gnu/\n".format(cpio_prefix)
                        line += "\n"
                        line += "cd ./{}\n".format(cpio_prefix)
                        line += "find . | cpio -o --format=newc > ../{}.cpio\n".format(cpio_prefix)
                        line += "cd .."
                        if need_gzip:
                            line += "gzip -f {}.cpio\n".format(cpio_prefix)
                            line += "mv {}.cpio.gz {}.cpio\n".format(cpio_prefix, cpio_prefix)
                        pass
                    continue
                
                
                newcontent += line
            newcontent += "-s\n"
        
        with open(run_sh, "wt", encoding="utf-8") as fp:
            fp.write(newcontent)
    
    # generate exp.c
    with open("exp.c", "wt", encoding="utf-8") as fp:
        ctx.vlog("template-command --> Generate exp.c.")
        fp.write("""
#define LOG_ENABLE 1            // 打印日志
#define DEBUG 0                 // 打印函数日志

#define USERFAULT_ENABLE 1      // 编译userfault处理相关代码
#define MSG_MSG_ENABLE 1        // 编译msg_msg相关的函数
#define USER_KEY_ENABLE 1       // 编译user_key_payload相关的函数
#define MODPROBE_ENABLE 1       // 编译modprobe_path相关的函数
#define ROOMT_ME_ENABLE 0       // 不编译root_me相关代码
#define ASSEMBLY_INTEL 0        // 不使用intel汇编 开启时需要加上编译参数 -masm=intel

#define G_BUFFER 1              // 使用G_BUFFER
#define USERFAULT_CONTROL 1     // 使用全局变量控制userfaultfd

#include "pwn.h"

int main()
{
    printf("hello world!");
    return 0;
}

""")
    

def generate_kernel_exp(ctx, directory):
    need_gzip = 0
    ko_name = ""
    cpio_prefix = ""
    run_sh = ""
    
    for f in os.listdir("."):
        if f == "bzImage" and os.path.isfile(f) and not os.path.exists("vmlinux"):
            ctx.vlog("template-command --> Detect bzImage in current directory.")
            try:
                wget("https://raw.githubusercontent.com/torvalds/linux/master/scripts/extract-vmlinux", save=True, timeout=300)
                os.chmod("./extract-vmlinux", 0o755)
                os.system("./extract-vmlinux bzImage > vmlinux")
                ctx.vlog("template-command --> Extract vmlinux from bzImage.")
                os.unlink("./extract-vmlinux")
            except:
                ctx.verrlog("template-command --> Extrace vmlinux failed!")
            
        
        elif f.endswith(".ko"):
            ko_name = f
        
        elif f.endswith(".cpio"):
            shutil.copyfile(f, f+".bk")
            cpio_prefix = f.rstrip(".cpio")
            if b"gzip" in subprocess.check_output(["file", f]):
                need_gzip = 1
                os.rename(f, f+".gz")
        
        elif f.endswith(".cpio.gz"):
            shutil.copyfile(f, f+".bk")
            need_gzip = 1
            cpio_prefix = f.rstrip(".cpio.gz")
        
        elif f.endswith(".sh") and f in ("run.sh", "start.sh", "boot.sh", "launch.sh"):
            os.chmod(f, 0o755)
            shutil.copyfile(f, f+".bk")
            run_sh = f
    
    _prepare_files_for_kernel_exp(ctx, ko_name, run_sh, cpio_prefix, need_gzip)


@click.command(name='template', short_help="Generate template file by pwncli.")
@click.argument('filetype', type=str, default=None, required=False, nargs=1)
@pass_environ
def cli(ctx, filetype):
    """
    FILETYPE: The type of exp file

    \b
    pwncli template cli
    pwncli template lib
    pwncli template pwn
    """
    ctx.verbose = 2
    if not ctx.cli_mode:
        ctx.abort("template-command --> Please use the command in cli instead of a lib!")
    
    if filetype == "lib" or (filetype and "lib".startswith(filetype)):
        generate_lib_exp(ctx, ".")
    elif filetype == "pwn" or (filetype and "pwn".startswith(filetype)):
        generate_pwn_exp(ctx, ".")
    elif filetype == "kernel" or (filetype and "kernel".startswith(filetype)):
        generate_kernel_exp(ctx, ".")
    else:
        if filetype and not "cli".startswith(filetype):
            ctx.abort("template-command --> The choice of filetype is ['cli', 'lib', 'pwn', 'kernel']!")
        generate_cli_exp(ctx, ".")
