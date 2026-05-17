from pwn import context, unpack

from pwncli import obstack_chunk_struct, obstack_struct


class TestObstackChunkStruct:
    def test_obstack_chunk_struct_amd64(self):
        with context.local(bits=64):
            chunk = obstack_chunk_struct()
            chunk.limit = 0x1122334455667788
            chunk.prev = 0x8877665544332211
            chunk.contents = b"ABCD"

            data = bytes(chunk)
            assert obstack_chunk_struct.sizeof(64) == 0x10
            assert len(chunk) == 0x14
            assert unpack(data[:8], 64) == 0x1122334455667788
            assert unpack(data[8:16], 64) == 0x8877665544332211
            assert data[16:20] == b"ABCD"

    def test_obstack_chunk_struct_i386(self):
        with context.local(bits=32):
            chunk = obstack_chunk_struct()
            chunk.limit = 0x11223344
            chunk.prev = 0x55667788
            chunk.contents = b"WXYZ"

            data = bytes(chunk)
            assert obstack_chunk_struct.sizeof(32) == 0x8
            assert len(chunk) == 0xc
            assert unpack(data[:4], 32) == 0x11223344
            assert unpack(data[4:8], 32) == 0x55667788
            assert data[8:12] == b"WXYZ"


class TestObstackStruct:
    def test_obstack_struct_amd64(self):
        with context.local(bits=64):
            obstack = obstack_struct()
            obstack.chunk_size = 0x1234567890ABCDEF
            obstack.chunk = 0x1111111122222222
            obstack.object_base = 0x3333333344444444
            obstack.next_free = 0x5555555566666666
            obstack.chunk_limit = 0x7777777788888888
            obstack.tempptr = 0x99999999AAAAAAAA
            obstack.alignment_mask = 0x10
            obstack.chunkfun = 0xBBBBBBBBCCCCCCCC
            obstack.freefun = 0xDDDDDDDDEEEEEEEE
            obstack.extra_arg = 0x1234123412341234
            obstack.use_extra_arg = 1
            obstack.maybe_empty_object = 1
            obstack.alloc_failed = 0

            data = bytes(obstack)
            assert obstack_struct.sizeof(64) == 0x58
            assert len(obstack) == 0x58
            assert unpack(data[:8], 64) == 0x1234567890ABCDEF
            assert unpack(data[0x28:0x30], 64) == 0x99999999AAAAAAAA
            assert unpack(data[0x38:0x40], 64) == 0xBBBBBBBBCCCCCCCC
            assert unpack(data[0x50:0x54], 32) == 0x3
            assert obstack.tempint == 0x99999999AAAAAAAA
            assert obstack.use_extra_arg == 1
            assert obstack.maybe_empty_object == 1
            assert obstack.alloc_failed == 0

    def test_obstack_struct_i386(self):
        with context.local(bits=32):
            obstack = obstack_struct()
            obstack.chunk_size = 0x11223344
            obstack.chunk = 0x55667788
            obstack.tempint = 0x12345678
            obstack.use_extra_arg = 1
            obstack.maybe_empty_object = 0
            obstack.alloc_failed = 1

            data = bytes(obstack)
            assert obstack_struct.sizeof(32) == 0x2c
            assert len(obstack) == 0x2c
            assert unpack(data[:4], 32) == 0x11223344
            assert unpack(data[4:8], 32) == 0x55667788
            assert unpack(data[0x14:0x18], 32) == 0x12345678
            assert unpack(data[0x28:0x2c], 32) == 0x5
            assert obstack.tempptr == 0x12345678
            assert obstack.use_extra_arg == 1
            assert obstack.maybe_empty_object == 0
            assert obstack.alloc_failed == 1
