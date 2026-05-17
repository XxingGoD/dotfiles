#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : cmd_patchelf.py
@Time    : 2021/11/23 23:50:09
@Author  : Roderick Chan
@Email   : roderickchan@foxmail.com
@Desc    : patchelf subcommand
'''


import os
import re
import shutil
import sys

import click
from pwn import which, yesno

from pwncli.cli import pass_environ
from pwncli.utils.config import try_get_config_data_by_key
from pwncli.utils.misc import _get_elf_arch_info


def get_arch_info_from_file(ctx, filepath):
    arch = _get_elf_arch_info(filepath)
    if arch in ("i386", "amd64"):
        return arch
    else:
        ctx.verrlog("patchelf-command --> Unsupported file, arch info:{}".format(arch))
        ctx.abort()


def _find_libc_ld_in_local_dir(directory, archinfo):
    """Recursively find libc and ld files in the given directory."""
    libc_file = ""
    ld_file = ""
    for root, dirs, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            if not os.path.isfile(full_path):
                continue
            try:
                with open(full_path, "rb") as fp:
                    data = fp.read(4)
                    if data != b"\x7fELF":
                        continue
            except:
                continue
            if f.startswith("libc.so") or f.startswith("libc-2."):
                libc_file = full_path
            elif f.startswith("ld.so") or f.startswith("ld-2.") or f.startswith("ld-linux"):
                ld_file = full_path
        if libc_file and ld_file:
            break
    if libc_file and not ld_file:
        ld_dir = os.path.dirname(libc_file)
        for f in os.listdir(ld_dir):
            if f.startswith("ld.so") or f.startswith("ld-2.") or f.startswith("ld-linux"):
                ld_file = os.path.join(ld_dir, f)
                break
    return libc_file, ld_file


def _download_from_glibc_all_in_one(ctx, libc_so, archinfo, libc_dirname):
    download_info = ""
    with open(libc_so, "rt", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    
    _match = re.search(r"GLIBC\s(\d\.\d\d-\dubuntu[\d\.]*)\)", data)
    if _match:
        download_info = _match.groups()[0] + "_" + archinfo
        download_path = os.path.split(libc_dirname)[0]
        cmd = "cd {} && {} {}".format(download_path, "./download", download_info)
        os.system(cmd)
        ctx.vlog("patchelf-command --> Exec cmd: {}".format(cmd))
        return download_info[:4]
    else:
        ctx.abort("patchelf-command --> Cannot get glibc version, please specify libc_version or check your libc.so file: {}".format(libc_so))
    

def _copy_to_current_dir(ctx, src_path, cwd):
    basename = os.path.basename(src_path)
    dst_path = os.path.join(cwd, basename)
    if not os.path.exists(dst_path):
        shutil.copy2(src_path, dst_path)
        ctx.vlog("patchelf-command --> Copy '{}' to current directory".format(src_path))
    else:
        ctx.vlog("patchelf-command --> Reuse '{}' in current directory".format(dst_path))
    return os.path.join(".", basename)


@click.command(name='patchelf', short_help="Patchelf executable file with glibc-all-in-one or current directory libs.")
@click.argument('filename', type=str, required=True, nargs=1)
@click.argument("libc-version", required=False, nargs=1, type=str)
@click.option('-b', '--back', '--back-up', "back_up", is_flag=True, help="Backup target file or not.")
@click.option('-f', '--filter', '--filter-string', "filter_string", default=[], type=str, multiple=True, help="Add filter condition.")
@click.option('-s', '-l', '--libc-so', "libc_so", type=click.Path(exists=True, file_okay=True), default=".", required=False, help="The libc.so.6 file, libc_version will be ignored when libc.so.6 file specified.")
@click.option('-v', '--verbose', count=True, help="Show more info or not.")
@pass_environ
def cli(ctx, filename, libc_version, back_up, filter_string, verbose, libc_so):
    """FILENAME: ELF executable filename.\n
    LIBC_VERSION: Libc version.

    \b
    pwncli patchelf ./filename 2.23 -b

    To execute:

        patchelf --set-interpreter ./ld-2.23.so ./pwn

        patchelf --replace-needed libc.so.6 ./libc-2.23.so ./pwn
    """
    if not ctx.verbose:
        ctx.verbose = verbose
    if verbose:
        ctx.vlog("patchelf-command --> Open 'verbose' mode")
    
    # check file name
    if not os.path.isfile(os.path.abspath(filename)):
        ctx.abort("patchelf-command --> Filename '{}' error!".format(filename))
    
    # check patchelf
    if not which('patchelf'):
        ctx.abort("patchelf-command --> Cannot find 'patchelf', please install it first!")
    
    filename = os.path.abspath(filename)
    archinfo = get_arch_info_from_file(ctx, filename)

    # backup first
    if back_up:
        cmd = "cp {} {}".format(filename, filename+".bk")
        ctx.vlog("patchelf-command --> Backup file named: {}".format(filename+".bk"))
        os.system(cmd)

    # Mode priority: current dir > glibc-all-in-one
    use_local_mode = False
    cwd = os.getcwd()

    # Step 1: Try to find libc/ld in current directory first
    libcfile_path, ldfile_path = _find_libc_ld_in_local_dir(cwd, archinfo)
    if libcfile_path and ldfile_path:
        use_local_mode = True
        ctx.vlog("patchelf-command --> Found libc/ld in current directory")
        if libcfile_path.startswith(cwd):
            libcfile_path = os.path.relpath(libcfile_path, cwd)
        if ldfile_path.startswith(cwd):
            ldfile_path = os.path.relpath(ldfile_path, cwd)

    if use_local_mode:
        ctx.vlog("patchelf-command --> Found libc: {}".format(libcfile_path))
        ctx.vlog("patchelf-command --> Found ld: {}".format(ldfile_path))
    else:
        # Mode 1: glibc-all-in-one
        if not libc_version:
            ctx.abort("patchelf-command --> Please specify libc_version or put libc/ld files in current directory.")
        
        libs_dirname = try_get_config_data_by_key(ctx.config_data, "patchelf", "libs_dir")
        if not libs_dirname:
            libs_dirname = os.path.join(os.environ['HOME'],"glibc-all-in-one/libs")
        
        if libs_dirname.startswith("~"):
            libs_dirname = os.path.expanduser(libs_dirname)
        
        libs_dirname = os.path.abspath(os.path.realpath(libs_dirname)).rstrip("/")
        
        # check libc_dirname
        if not os.path.exists(libs_dirname) or not os.path.isdir(libs_dirname):
            ctx.verrlog("patchelf-command --> Libs dir '{}' not exists!".format(libs_dirname))
            if yesno("clone glibc-all-in-one from github?"):
                if 0 != os.system("git clone https://github.com/matrix1001/glibc-all-in-one.git ~/glibc-all-in-one"):
                    ctx.abort("patchelf-command --> Execute cmd: git clone https://github.com/matrix1001/glibc-all-in-one.git ~/ failed!")
                ctx.vlog2("patchelf-command --> Execute cmd: git clone https://github.com/matrix1001/glibc-all-in-one.git ~/ success!")
                libs_dirname = os.path.join(os.environ['HOME'],"glibc-all-in-one/libs")
            else:
                sys.exit(1)
        
        if not libs_dirname.endswith("glibc-all-in-one/libs"):
            ctx.abort("patchelf-command --> Unsupported libc_dirname, must end with glibc-all-in-one/libs.")

        ctx.vlog("patchelf-command --> Now libs_dirname used is: {}".format(libs_dirname))

        if os.path.exists(libc_so) and os.path.isfile(libc_so):
            ctx.vlog2("patchelf-command --> Libc_so is specified, libc_version would be reset.")
            libc_version = _download_from_glibc_all_in_one(ctx, libc_so, archinfo, libs_dirname)

        # check libc_version
        if not re.search(r"^\d\.\d\d$", libc_version):
            ctx.abort("patchelf-command --> Invalid libc_version: {}".format(libc_version))

        def _filter_dir(_d):
            for _i in filter_string:
                    if _i not in _d:
                        return False
            if (archinfo in _d) and (os.path.isdir(os.path.join(libs_dirname, _d))):
                return True
            return False

        subdirs = list(filter(_filter_dir, os.listdir(libs_dirname)))
        if not subdirs or len(subdirs) == 0:
            ctx.abort("patchelf-command --> Do not find the matched dirctories in {}, with libc_version: {}, filter-string:{}".format(libs_dirname, libc_version, filter_string))

        subdirs.sort()
        
        has_versions = [x[:4] for x in subdirs]
        
        if not has_versions or len(has_versions) == 0 or libc_version not in has_versions:
            ctx.abort("patchelf-command --> Do not have the libc version of {}, only have {}!".format(libc_version, has_versions))
        
        # execute patchelf
        subdirname = subdirs[has_versions.index(libc_version)]
        last_dirname = os.path.join(libs_dirname, subdirname)
        ctx.vlog("patchelf-command --> The dirname of libs using by patchelf: {}".format(last_dirname))

        ldfile_path = os.path.join(last_dirname, 'ld-{}.so'.format(libc_version))
        if not os.path.exists(ldfile_path):
            ldfile_path = os.path.join(last_dirname, 'ld-linux-x86-64.so.2')
            if not os.path.exists(ldfile_path):
                ctx.abort("patchelf-command --> The ld file: {} not exists!".format(ldfile_path))
        
        libcfile_path = os.path.join(last_dirname, 'libc-{}.so'.format(libc_version))
        if not os.path.exists(libcfile_path):
            libcfile_path = os.path.join(last_dirname, 'libc.so.6')
            if not os.path.exists(libcfile_path):
                ctx.abort("patchelf-command --> The libc file: {} not exists!".format(libcfile_path))

        ldfile_path = _copy_to_current_dir(ctx, ldfile_path, cwd)
        libcfile_path = _copy_to_current_dir(ctx, libcfile_path, cwd)
    
    cmd1 = "patchelf --set-interpreter {} {}".format(ldfile_path, filename)
    ctx.vlog("patchelf-command --> Execute cmd: {}".format(cmd1))
    os.system(cmd1)

    cmd2 = "patchelf --replace-needed libc.so.6 {} {}".format(libcfile_path, filename)
    ctx.vlog("patchelf-command --> Execute cmd: {}".format(cmd2))
    os.system(cmd2)

    print("The output of ldd:")
    os.system("ldd {}".format(filename))
    
