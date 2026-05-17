#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : ld_so.py
@Time    : 2026/04/27
@Desc    : Helpers for ld.so related structures used in House of Banana
'''

from pwn import context, error, pack

DT_NUM = 38
DT_THISPROCNUM = 0
DT_VERSIONTAGNUM = 16
DT_EXTRANUM = 3
DT_VALNUM = 12
DT_ADDRNUM = 11

DL_NNS = 16

DT_FINI = 13
DT_FINI_ARRAY = 26
DT_FINI_ARRAYSZ = 28

LINK_MAP_L_INFO_COUNT = DT_NUM + DT_THISPROCNUM + DT_VERSIONTAGNUM + DT_EXTRANUM + DT_VALNUM + DT_ADDRNUM

__all__ = [
    "DL_NNS",
    "DT_FINI",
    "DT_FINI_ARRAY",
    "DT_FINI_ARRAYSZ",
    "LINK_MAP_L_INFO_COUNT",
    "Elf_Dyn_struct",
    "link_namespaces_struct",
    "link_namespace_struct",
    "link_map_struct",
    "r_debug_struct",
    "rtld_global_struct",
    "rtld_lock_recursive_struct",
    "unique_sym_struct",
    "unique_sym_table_struct",
]


def _require_bits(bits):
    if bits is None:
        bits = context.bits
    assert bits in (32, 64), "bits must be 32 or 64!"
    return bits


def _ptr_size(bits):
    return _require_bits(bits) // 8


def _rtld_lock_recursive_size(bits):
    bits = _require_bits(bits)
    return 40 if bits == 64 else 24


class _StructBase(object):

    vars_: list[str] = []
    length: dict[str, int] = {}

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
            if isinstance(value, (bytes, bytearray)):
                structure.append(" {}: {!r}".format(item, bytes(value)))
            elif isinstance(value, (list, tuple)):
                structure.append(" {}: {!r}".format(item, list(value)))
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

    def _pack_iterable(self, val, value):
        slots = self.length[val] // context.bytes
        assert self.length[val] % context.bytes == 0, "field %r does not support iterable values" % val
        assert len(value) <= slots, "too many values for field %r" % val
        structure = b""
        for item in value:
            if isinstance(item, str):
                item = item.encode("latin-1")
            if isinstance(item, (bytes, bytearray)):
                structure += bytes(item).ljust(context.bytes, b"\x00")
            elif hasattr(item, "__bytes__") and not isinstance(item, int):
                structure += bytes(item).ljust(context.bytes, b"\x00")
            else:
                structure += pack(item, context.bytes * 8)
        return structure.ljust(self.length[val], b"\x00")

    def __bytes__(self):
        structure = b""
        for val in self.vars_:
            value = getattr(self, val)
            if isinstance(value, str):
                value = value.encode("latin-1")
            if isinstance(value, (list, tuple)):
                structure += self._pack_iterable(val, value)
            elif isinstance(value, (bytes, bytearray)):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif self.length[val] > 0:
                structure += pack(value, self.length[val] * 8)
        return structure

    def struntil(self, v):
        if v not in self.vars_:
            return b""
        structure = b""
        for val in self.vars_:
            value = getattr(self, val)
            if isinstance(value, str):
                value = value.encode("latin-1")
            if isinstance(value, (list, tuple)):
                structure += self._pack_iterable(val, value)
            elif isinstance(value, (bytes, bytearray)):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif self.length[val] > 0:
                structure += pack(value, self.length[val] * 8)
            if val == v:
                break
        return structure


class Elf_Dyn_struct(_StructBase):

    d_tag: int | bytes | bytearray
    d_val: int | bytes | bytearray

    vars_ = [
        "d_tag",
        "d_val",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "d_tag": length,
            "d_val": length,
        }

    @property
    def d_ptr(self) -> int | bytes | bytearray:
        return self.d_val

    @d_ptr.setter
    def d_ptr(self, value: int | bytes | bytearray):
        self.d_val = value

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : d_tag ")
        print("  {} : d_val/d_ptr ".format(hex(ptr)))


class link_namespace_struct(_StructBase):

    _ns_loaded: int | bytes | bytearray
    _ns_nloaded: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    _ns_main_searchlist: int | bytes | bytearray
    _ns_global_scope_alloc: int | bytes | bytearray
    _ns_global_scope_pending_adds: int | bytes | bytearray
    libc_map: int | bytes | bytearray

    vars_ = [
        "_ns_loaded",
        "_ns_nloaded",
        "_pad0",
        "_ns_main_searchlist",
        "_ns_global_scope_alloc",
        "_ns_global_scope_pending_adds",
        "libc_map",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "_ns_loaded": length,
            "_ns_nloaded": 4,
            "_pad0": max(length - 4, 0),
            "_ns_main_searchlist": length,
            "_ns_global_scope_alloc": 4,
            "_ns_global_scope_pending_adds": 4,
            "libc_map": length,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : _ns_loaded ")
        print("  {} : _ns_nloaded ".format(hex(ptr)))
        if ptr == 8:
            print("  0xc : _pad0 ")
        print("  {} : _ns_main_searchlist ".format(hex(0x10 if ptr == 8 else 0x8)))
        print("  {} : _ns_global_scope_alloc ".format(hex(0x18 if ptr == 8 else 0xc)))
        print("  {} : _ns_global_scope_pending_adds ".format(hex(0x1c if ptr == 8 else 0x10)))
        print("  {} : libc_map ".format(hex(0x20 if ptr == 8 else 0x14)))


class rtld_lock_recursive_struct(_StructBase):

    mutex: int | bytes | bytearray

    vars_ = [
        "mutex",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "mutex": _rtld_lock_recursive_size(length * 8),
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        print("arch :", arch)
        print("  0x0 : mutex ")


class r_debug_struct(_StructBase):

    r_version: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    r_map: int | bytes | bytearray
    r_brk: int | bytes | bytearray
    r_state: int | bytes | bytearray
    _pad1: int | bytes | bytearray
    r_ldbase: int | bytes | bytearray

    vars_ = [
        "r_version",
        "_pad0",
        "r_map",
        "r_brk",
        "r_state",
        "_pad1",
        "r_ldbase",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "r_version": 4,
            "_pad0": max(length - 4, 0),
            "r_map": length,
            "r_brk": length,
            "r_state": 4,
            "_pad1": max(length - 4, 0),
            "r_ldbase": length,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : r_version ")
        if ptr == 8:
            print("  0x4 : _pad0 ")
        print("  {} : r_map ".format(hex(0x8 if ptr == 8 else 0x4)))
        print("  {} : r_brk ".format(hex(0x10 if ptr == 8 else 0x8)))
        print("  {} : r_state ".format(hex(0x18 if ptr == 8 else 0xc)))
        if ptr == 8:
            print("  0x1c : _pad1 ")
        print("  {} : r_ldbase ".format(hex(0x20 if ptr == 8 else 0x10)))


class unique_sym_struct(_StructBase):

    hashval: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    name: int | bytes | bytearray
    sym: int | bytes | bytearray
    map: int | bytes | bytearray

    vars_ = [
        "hashval",
        "_pad0",
        "name",
        "sym",
        "map",
    ]

    @staticmethod
    def _update_var(length):
        return {
            "hashval": 4,
            "_pad0": max(length - 4, 0),
            "name": length,
            "sym": length,
            "map": length,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : hashval ")
        if ptr == 8:
            print("  0x4 : _pad0 ")
        print("  {} : name ".format(hex(0x8 if ptr == 8 else 0x4)))
        print("  {} : sym ".format(hex(0x10 if ptr == 8 else 0x8)))
        print("  {} : map ".format(hex(0x18 if ptr == 8 else 0xc)))


class unique_sym_table_struct(_StructBase):

    lock: int | bytes | bytearray | rtld_lock_recursive_struct
    entries: int | bytes | bytearray
    size: int | bytes | bytearray
    n_elements: int | bytes | bytearray
    free: int | bytes | bytearray

    vars_ = [
        "lock",
        "entries",
        "size",
        "n_elements",
        "free",
    ]

    def __init__(self):
        super().__init__()
        self.lock = rtld_lock_recursive_struct()

    @staticmethod
    def _update_var(length):
        return {
            "lock": rtld_lock_recursive_struct.sizeof(length * 8),
            "entries": length,
            "size": length,
            "n_elements": length,
            "free": length,
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        bits = 64 if arch == "amd64" else 32
        lock_size = rtld_lock_recursive_struct.sizeof(bits)
        ptr = bits // 8
        print("arch :", arch)
        print("  0x0 : lock ")
        print("  {} : entries ".format(hex(lock_size)))
        print("  {} : size ".format(hex(lock_size + ptr)))
        print("  {} : n_elements ".format(hex(lock_size + ptr * 2)))
        print("  {} : free ".format(hex(lock_size + ptr * 3)))


class link_namespaces_struct(_StructBase):

    _ns_loaded: int | bytes | bytearray
    _ns_nloaded: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    _ns_main_searchlist: int | bytes | bytearray
    _ns_global_scope_alloc: int | bytes | bytearray
    _ns_global_scope_pending_adds: int | bytes | bytearray
    libc_map: int | bytes | bytearray
    _ns_unique_sym_table: int | bytes | bytearray | unique_sym_table_struct
    _ns_debug: int | bytes | bytearray | r_debug_struct

    vars_ = [
        "_ns_loaded",
        "_ns_nloaded",
        "_pad0",
        "_ns_main_searchlist",
        "_ns_global_scope_alloc",
        "_ns_global_scope_pending_adds",
        "libc_map",
        "_ns_unique_sym_table",
        "_ns_debug",
    ]

    def __init__(self):
        super().__init__()
        self._ns_unique_sym_table = unique_sym_table_struct()
        self._ns_debug = r_debug_struct()

    @staticmethod
    def _update_var(length):
        return {
            "_ns_loaded": length,
            "_ns_nloaded": 4,
            "_pad0": max(length - 4, 0),
            "_ns_main_searchlist": length,
            "_ns_global_scope_alloc": 4,
            "_ns_global_scope_pending_adds": 4,
            "libc_map": length,
            "_ns_unique_sym_table": unique_sym_table_struct.sizeof(length * 8),
            "_ns_debug": r_debug_struct.sizeof(length * 8),
        }

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        bits = 64 if arch == "amd64" else 32
        ptr = bits // 8
        print("arch :", arch)
        print("  0x0 : _ns_loaded ")
        print("  {} : _ns_nloaded ".format(hex(ptr)))
        if ptr == 8:
            print("  0xc : _pad0 ")
        print("  {} : _ns_main_searchlist ".format(hex(0x10 if ptr == 8 else 0x8)))
        print("  {} : _ns_global_scope_alloc ".format(hex(0x18 if ptr == 8 else 0xc)))
        print("  {} : _ns_global_scope_pending_adds ".format(hex(0x1c if ptr == 8 else 0x10)))
        print("  {} : libc_map ".format(hex(0x20 if ptr == 8 else 0x14)))
        print("  {} : _ns_unique_sym_table ".format(hex(0x28 if ptr == 8 else 0x18)))
        print("  {} : _ns_debug ".format(hex(0x70 if ptr == 8 else 0x40)))


class link_map_struct(_StructBase):

    l_addr: int | bytes | bytearray
    l_name: int | bytes | bytearray
    l_ld: int | bytes | bytearray
    l_next: int | bytes | bytearray
    l_prev: int | bytes | bytearray
    l_real: int | bytes | bytearray
    l_ns: int | bytes | bytearray
    l_libname: int | bytes | bytearray
    l_info: list[int] | tuple[int, ...] | bytes | bytearray
    l_phdr: int | bytes | bytearray
    l_entry: int | bytes | bytearray
    l_phnum: int | bytes | bytearray
    l_ldnum: int | bytes | bytearray
    _pad0: int | bytes | bytearray
    suffix = b""

    vars_ = [
        "l_addr",
        "l_name",
        "l_ld",
        "l_next",
        "l_prev",
        "l_real",
        "l_ns",
        "l_libname",
        "l_info",
        "l_phdr",
        "l_entry",
        "l_phnum",
        "l_ldnum",
        "_pad0",
    ]

    def __init__(self):
        super().__init__()
        self.l_info = [0] * LINK_MAP_L_INFO_COUNT
        self.suffix = b""

    @staticmethod
    def _update_var(length):
        return {
            "l_addr": length,
            "l_name": length,
            "l_ld": length,
            "l_next": length,
            "l_prev": length,
            "l_real": length,
            "l_ns": length,
            "l_libname": length,
            "l_info": LINK_MAP_L_INFO_COUNT * length,
            "l_phdr": length,
            "l_entry": length,
            "l_phnum": 2,
            "l_ldnum": 2,
            "_pad0": max(length - 4, 0),
        }

    def __bytes__(self):
        suffix = self.suffix
        if isinstance(suffix, str):
            suffix = suffix.encode("latin-1")
        elif not isinstance(suffix, (bytes, bytearray)):
            suffix = bytes(suffix)
        return super().__bytes__() + bytes(suffix)

    @staticmethod
    def l_info_offset(index: int, bits=None):
        if bits is None:
            bits = context.bits
        assert bits in (32, 64), "bits must be 32 or 64!"
        assert 0 <= index < LINK_MAP_L_INFO_COUNT, "l_info index out of range"
        return (8 if bits == 64 else 4) * 8 + index * (bits // 8)

    def _normalized_l_info(self):
        value = self.l_info
        if isinstance(value, (list, tuple)):
            items = list(value)
        elif isinstance(value, str):
            raw = value.encode("latin-1")
            items = [int.from_bytes(raw[i:i + context.bytes].ljust(context.bytes, b"\x00"), "little")
                     for i in range(0, min(len(raw), LINK_MAP_L_INFO_COUNT * context.bytes), context.bytes)]
        elif isinstance(value, (bytes, bytearray)):
            raw = bytes(value)
            items = [int.from_bytes(raw[i:i + context.bytes].ljust(context.bytes, b"\x00"), "little")
                     for i in range(0, min(len(raw), LINK_MAP_L_INFO_COUNT * context.bytes), context.bytes)]
        else:
            items = [0] * LINK_MAP_L_INFO_COUNT
        if len(items) < LINK_MAP_L_INFO_COUNT:
            items.extend([0] * (LINK_MAP_L_INFO_COUNT - len(items)))
        return items[:LINK_MAP_L_INFO_COUNT]

    def get_l_info(self, index: int):
        assert 0 <= index < LINK_MAP_L_INFO_COUNT, "l_info index out of range"
        return self._normalized_l_info()[index]

    def set_l_info(self, index: int, value: int):
        assert 0 <= index < LINK_MAP_L_INFO_COUNT, "l_info index out of range"
        items = self._normalized_l_info()
        items[index] = value
        self.l_info = items

    @property
    def l_info_dt_fini(self):
        return self.get_l_info(DT_FINI)

    @l_info_dt_fini.setter
    def l_info_dt_fini(self, value: int):
        self.set_l_info(DT_FINI, value)

    @property
    def l_info_dt_fini_array(self):
        return self.get_l_info(DT_FINI_ARRAY)

    @l_info_dt_fini_array.setter
    def l_info_dt_fini_array(self, value: int):
        self.set_l_info(DT_FINI_ARRAY, value)

    @property
    def l_info_dt_fini_arraysz(self):
        return self.get_l_info(DT_FINI_ARRAYSZ)

    @l_info_dt_fini_arraysz.setter
    def l_info_dt_fini_arraysz(self, value: int):
        self.set_l_info(DT_FINI_ARRAYSZ, value)

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        ptr = 8 if arch == "amd64" else 4
        print("arch :", arch)
        print("  0x0 : l_addr ")
        print("  {} : l_name ".format(hex(ptr)))
        print("  {} : l_ld ".format(hex(ptr * 2)))
        print("  {} : l_next ".format(hex(ptr * 3)))
        print("  {} : l_prev ".format(hex(ptr * 4)))
        print("  {} : l_real ".format(hex(ptr * 5)))
        print("  {} : l_ns ".format(hex(ptr * 6)))
        print("  {} : l_libname ".format(hex(ptr * 7)))
        print("  {} : l_info[0] ".format(hex(ptr * 8)))
        print("  {} : l_info[DT_FINI] ".format(hex(link_map_struct.l_info_offset(DT_FINI, 64 if ptr == 8 else 32))))
        print("  {} : l_info[DT_FINI_ARRAY] ".format(hex(link_map_struct.l_info_offset(DT_FINI_ARRAY, 64 if ptr == 8 else 32))))
        print("  {} : l_info[DT_FINI_ARRAYSZ] ".format(hex(link_map_struct.l_info_offset(DT_FINI_ARRAYSZ, 64 if ptr == 8 else 32))))
        print("  {} : l_phdr ".format(hex(ptr * 8 + LINK_MAP_L_INFO_COUNT * ptr)))
        print("  {} : l_entry ".format(hex(ptr * 9 + LINK_MAP_L_INFO_COUNT * ptr)))
        print("  {} : l_phnum ".format(hex(ptr * 10 + LINK_MAP_L_INFO_COUNT * ptr)))
        print("  {} : l_ldnum ".format(hex(ptr * 10 + LINK_MAP_L_INFO_COUNT * ptr + 0x2)))
        if ptr == 8:
            print("  {} : _pad0 ".format(hex(ptr * 10 + LINK_MAP_L_INFO_COUNT * ptr + 0x4)))


class rtld_global_struct(_StructBase):

    _dl_ns: list[object] | tuple[object, ...] | bytes | bytearray
    _dl_nns: int | bytes | bytearray
    _dl_load_lock: int | bytes | bytearray | rtld_lock_recursive_struct
    _dl_load_write_lock: int | bytes | bytearray | rtld_lock_recursive_struct
    _dl_load_adds: int | bytes | bytearray
    _dl_initfirst: int | bytes | bytearray
    _dl_profile_map: int | bytes | bytearray
    _dl_num_relocations: int | bytes | bytearray
    _dl_num_cache_relocations: int | bytes | bytearray
    _dl_all_dirs: int | bytes | bytearray
    _dl_rtld_map: int | bytes | bytearray | link_map_struct
    suffix = b""

    vars_ = [
        "_dl_ns",
        "_dl_nns",
        "_dl_load_lock",
        "_dl_load_write_lock",
        "_dl_load_adds",
        "_dl_initfirst",
        "_dl_profile_map",
        "_dl_num_relocations",
        "_dl_num_cache_relocations",
        "_dl_all_dirs",
        "_dl_rtld_map",
    ]

    def __init__(self):
        super().__init__()
        self._dl_ns = [link_namespaces_struct() for _ in range(DL_NNS)]
        self._dl_load_lock = rtld_lock_recursive_struct()
        self._dl_load_write_lock = rtld_lock_recursive_struct()
        self._dl_rtld_map = link_map_struct()
        self.suffix = b""

    @staticmethod
    def _update_var(length):
        return {
            "_dl_ns": DL_NNS * link_namespaces_struct.sizeof(length * 8),
            "_dl_nns": length,
            "_dl_load_lock": rtld_lock_recursive_struct.sizeof(length * 8),
            "_dl_load_write_lock": rtld_lock_recursive_struct.sizeof(length * 8),
            "_dl_load_adds": 8,
            "_dl_initfirst": length,
            "_dl_profile_map": length,
            "_dl_num_relocations": length,
            "_dl_num_cache_relocations": length,
            "_dl_all_dirs": length,
            "_dl_rtld_map": link_map_struct.sizeof(length * 8),
        }

    @staticmethod
    def dl_ns_entry_size(bits=None):
        return link_namespaces_struct.sizeof(_require_bits(bits))

    @staticmethod
    def dl_ns_offset(index=0, bits=None):
        bits = _require_bits(bits)
        assert 0 <= index < DL_NNS, "_dl_ns index out of range"
        return index * rtld_global_struct.dl_ns_entry_size(bits)

    @staticmethod
    def dl_nns_offset(bits=None):
        bits = _require_bits(bits)
        return DL_NNS * rtld_global_struct.dl_ns_entry_size(bits)

    @staticmethod
    def dl_load_lock_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_nns_offset(bits) + _ptr_size(bits)

    @staticmethod
    def dl_load_write_lock_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_load_lock_offset(bits) + rtld_lock_recursive_struct.sizeof(bits)

    @staticmethod
    def dl_load_adds_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_load_write_lock_offset(bits) + rtld_lock_recursive_struct.sizeof(bits)

    @staticmethod
    def dl_initfirst_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_load_adds_offset(bits) + 8

    @staticmethod
    def dl_profile_map_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_initfirst_offset(bits) + _ptr_size(bits)

    @staticmethod
    def dl_num_relocations_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_profile_map_offset(bits) + _ptr_size(bits)

    @staticmethod
    def dl_num_cache_relocations_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_num_relocations_offset(bits) + _ptr_size(bits)

    @staticmethod
    def dl_all_dirs_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_num_cache_relocations_offset(bits) + _ptr_size(bits)

    @staticmethod
    def dl_rtld_map_offset(bits=None):
        bits = _require_bits(bits)
        return rtld_global_struct.dl_all_dirs_offset(bits) + _ptr_size(bits)

    def _normalized_dl_ns(self):
        value = self._dl_ns
        if isinstance(value, (list, tuple)):
            items = list(value)
        elif isinstance(value, str):
            raw = value.encode("latin-1")
            entry_size = self.dl_ns_entry_size()
            items = [raw[i:i + entry_size] for i in range(0, min(len(raw), self.length["_dl_ns"]), entry_size)]
        elif isinstance(value, (bytes, bytearray)):
            raw = bytes(value)
            entry_size = self.dl_ns_entry_size()
            items = [raw[i:i + entry_size] for i in range(0, min(len(raw), self.length["_dl_ns"]), entry_size)]
        elif value == 0:
            items = []
        else:
            items = [value]
        if len(items) < DL_NNS:
            items.extend([link_namespaces_struct() for _ in range(DL_NNS - len(items))])
        return items[:DL_NNS]

    def get_dl_ns(self, index: int):
        assert 0 <= index < DL_NNS, "_dl_ns index out of range"
        return self._normalized_dl_ns()[index]

    def set_dl_ns(self, index: int, value):
        assert 0 <= index < DL_NNS, "_dl_ns index out of range"
        items = self._normalized_dl_ns()
        items[index] = value
        self._dl_ns = items

    def _pack_dl_ns(self):
        value = self._dl_ns
        total = self.length["_dl_ns"]
        entry_size = self.dl_ns_entry_size()
        if isinstance(value, str):
            return value.encode("latin-1").ljust(total, b"\x00")
        if isinstance(value, (bytes, bytearray)):
            return bytes(value).ljust(total, b"\x00")
        if isinstance(value, (list, tuple)):
            assert len(value) <= DL_NNS, "too many _dl_ns entries"
            structure = b""
            for item in value:
                if isinstance(item, str):
                    chunk = item.encode("latin-1")
                elif isinstance(item, (bytes, bytearray)):
                    chunk = bytes(item)
                elif hasattr(item, "__bytes__") and not isinstance(item, int):
                    chunk = bytes(item)
                else:
                    chunk = pack(item, context.bytes * 8)
                structure += chunk.ljust(entry_size, b"\x00")
            return structure.ljust(total, b"\x00")
        if hasattr(value, "__bytes__") and not isinstance(value, int):
            return bytes(value).ljust(total, b"\x00")
        return pack(value, context.bytes * 8).ljust(total, b"\x00")

    def __bytes__(self):
        structure = b""
        for val in self.vars_:
            if val == "_dl_ns":
                structure += self._pack_dl_ns()
                continue
            value = getattr(self, val)
            if isinstance(value, str):
                value = value.encode("latin-1")
            if isinstance(value, (list, tuple)):
                structure += self._pack_iterable(val, value)
            elif isinstance(value, (bytes, bytearray)):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif hasattr(value, "__bytes__") and not isinstance(value, int):
                structure += bytes(value).ljust(self.length[val], b"\x00")
            elif self.length[val] > 0:
                structure += pack(value, self.length[val] * 8)
        suffix = self.suffix
        if isinstance(suffix, str):
            suffix = suffix.encode("latin-1")
        elif not isinstance(suffix, (bytes, bytearray)):
            suffix = bytes(suffix)
        return structure + bytes(suffix)

    def struntil(self, v):
        if v not in self.vars_:
            return b""
        structure = b""
        for val in self.vars_:
            if val == "_dl_ns":
                structure += self._pack_dl_ns()
            else:
                value = getattr(self, val)
                if isinstance(value, str):
                    value = value.encode("latin-1")
                if isinstance(value, (list, tuple)):
                    structure += self._pack_iterable(val, value)
                elif isinstance(value, (bytes, bytearray)):
                    structure += bytes(value).ljust(self.length[val], b"\x00")
                elif hasattr(value, "__bytes__") and not isinstance(value, int):
                    structure += bytes(value).ljust(self.length[val], b"\x00")
                elif self.length[val] > 0:
                    structure += pack(value, self.length[val] * 8)
            if val == v:
                break
        return structure

    @staticmethod
    def show_struct(arch="amd64"):
        if arch not in ("amd64", "i386"):
            error("arch error, only i386 and amd64 supported!")
        bits = 64 if arch == "amd64" else 32
        print("arch :", arch)
        print("  0x0 : _dl_ns[0] ")
        print("  {} : _dl_ns[1] ".format(hex(rtld_global_struct.dl_ns_offset(1, bits))))
        print("  {} : _dl_nns ".format(hex(rtld_global_struct.dl_nns_offset(bits))))
        print("  {} : _dl_load_lock ".format(hex(rtld_global_struct.dl_load_lock_offset(bits))))
        print("  {} : _dl_load_write_lock ".format(hex(rtld_global_struct.dl_load_write_lock_offset(bits))))
        print("  {} : _dl_load_adds ".format(hex(rtld_global_struct.dl_load_adds_offset(bits))))
        print("  {} : _dl_initfirst ".format(hex(rtld_global_struct.dl_initfirst_offset(bits))))
        print("  {} : _dl_profile_map ".format(hex(rtld_global_struct.dl_profile_map_offset(bits))))
        print("  {} : _dl_num_relocations ".format(hex(rtld_global_struct.dl_num_relocations_offset(bits))))
        print("  {} : _dl_num_cache_relocations ".format(hex(rtld_global_struct.dl_num_cache_relocations_offset(bits))))
        print("  {} : _dl_all_dirs ".format(hex(rtld_global_struct.dl_all_dirs_offset(bits))))
        print("  {} : _dl_rtld_map ".format(hex(rtld_global_struct.dl_rtld_map_offset(bits))))
