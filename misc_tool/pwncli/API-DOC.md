# misc.py

## 数据处理

### int16
功能：`16`进制字符串转为十进制数字

示例：
```
x = int16("ff")
print(x)
# 255
```

### int8
功能：`8`进制字符串转为十进制数字

示例：
```
x = int8('77')
print(x)
# 63
```

### int2
功能：`2`进制字符串转为十进制数字

示例：
```
x = int2('1010')
print(x)
# 10
```

### int16_ex
功能：`16`进制字节或者字符串转为十进制数字

示例：
```
x = int16_ex(b"0xff")
y = int16_ex("0x10")
print(x, y)
# 255 16
```

### int8_ex
功能：`8`进制字节或者字符串转为十进制数字

示例：
```
x = int8_ex(b"77")
y = int8_ex("77")
print(x, y)
# 63 63
```

### int2_ex
功能：`2`进制字节或者字符串转为十进制数字

示例：
```
x = int2_ex(b"1010")
y = int2_ex("1010")
print(x, y)
# 10 10
```

### u16_ex
功能：将最多`2`个字节或者长度为`2`的字符串转换为整数，长度不足`2`的时候往左补`\x00`

示例：
```
x = u16_ex(b"a")
y = u16_ex("aa")
print(hex(x), hex(y))
# 0x61 0x6161
```

### float_hexstr2int

功能：



### protect_ptr

功能：将数据按`glibc2.32`的`tcache`加密规则（`safe-linking`）进行加密

参数：

+ `address`：对应`size`的`tcachebin`头节点
+ `next`：想加密的数据

返回值：一个整数

示例：

```python
>>> protect_ptr(0xdeadbeef,0xbeefdead)
3202495606
```

即：`(0xdeadbeef >> 12) ^ 0xbeefdead = 3202495606`

### reveal_ptr

功能：将数据按`glibc2.32`的`tcache`加密规则`（safe-linking）`进行解密，解出的是一个与加密前数据误差不大的值

参数：

+ 一个需要解密的地址

返回值：一个整数

示例：

```python
>>> reveal_ptr(3202495606) 
3202996971
>>> hex(3202996971)
'0xbee9daeb'
```

### generate_payload_for_connect

功能：将代表网络地址的数据根据套接字对应格式转化为`16`进制字节流

参数：

+ `ip(str)`：要转换的`ip`地址
+ `port(int)`：要转换的端口

返回值：一个整数

示例：

```python
>>> generate_payload_for_connect('127.0.0.1',5555)
b'\x02\x00\x15\xb3\x7f\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
```

## 数据接收

### recv_libc_addr

功能：当接收到`/x7f`或`/xf7`时，根据设置的arch自动将包含"`/x7f`"在内的前3个字节/前6个字节解包为一个整数。

功能：当接收到`/x7f`或`/xf7`时，根据设置的arch自动将包含`/x7f`或`/xf7`在内的前3个字节/前6个字节解包为一个整数

参数：

+ `io(tube)`：一般会默认设置好的进程号，默认为通过pwncli de/re ./pwnfile 命令行起得进程
+ `bits(int, optional)`：一般会默认设置好的架构位数。32位架构与64位架构选其一
+ `offset(int, optional)`：解包后的整数要减去的偏移

返回值： 一个整数



## 日志打印

### log_ex

功能：打印参数内容至终端标准输出，内容前有提示符`[*] INFO`

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

```python
打印一个字符串
>>log_msg = "hello_world"
>>log_ex(log_msg)
[*] INFO  hello_world

打印多个字符串
>>log_msg1 = "Hello"
>>log_msg2 = "Pwncli"
>>log_ex((log_msg1,log_msg2))
[*] INFO  ('hello', 'Pwncli')

利用格式化字符串
>>log_ex("hello %s,your age is %d","roderick",10)
[*] INFO  hello roderick,your age is 10
```

### log_ex_highlight

功能：打印参数内容至终端标准输出, 内容前面的提示符`[*] INFO`为白底绿字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

与`log_ex`的示例一致

### log2_ex

功能：打印参数内容至终端标准输出，内容前面的提示符为蓝色的`[#] IMPORTANT INFO`

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

```text
打印一个字符串
>>log_msg = "hello_world"
>>log2_ex(log_msg)
[#] IMPORTANT INFO  hello_world

打印多个字符串
>>log_msg1 = "Hello"
>>log_msg2 = "Pwncli"
>>log2_ex((log_msg1,log_msg2))
[#] IMPORTANT INFO  ('hello', 'Pwncli')

利用格式化字符串
>>log2_ex("hello %s,your age is %d","roderick",10)
[#] IMPORTANT INFO  hello roderick,your age is 10
```

### log2_ex_highlight

功能：打印参数内容至终端标准输出, 内容前面的提示符`[#] IMPORTANT INFO`为白底蓝字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

与`log2_ex`的示例一致

### warn_ex

功能：打印参数内容至终端标准输出, 内容前面的提示符`[*]WARN`为黄字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

```text
>>warn_ex("hello %s,your age is %d","roderick",10)
[*] WARN  hello roderick,your age is 10
```

### warn_ex_highlight

功能：打印参数内容至终端标准输出, 内容前面的提示符`[*]WARN[!] ERROR`为白底黄字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：无

### errlog_ex

功能：打印参数内容至终端标准输出, 内容前面的提示符`[!] ERROR`为红字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：

```text
>>errlog_ex("hello %s,your age is %d","roderick",10)
[!] ERROR  hello roderick,your age is 10
```

### errlog_ex_highlight

功能：打印参数内容至终端标准输出, 内容前面的提示符`[!] ERROR`为白底红字

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：无

### errlog_exit

功能：打印参数内容至终端标准错误, 内容前面的提示符`[!] ERROR`为红字，然后退出

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：无

### errlog_ex_highlight_exit

功能：打印参数内容至终端标准错误, 内容前面的提示符`[!] ERROR`为白底红字，然后退出

参数：

+ `msg`：要输出内容, 可利用格式化字符串。如果需要输出多个内容，则需要用括号将参数括起来

返回值：无

示例：无

### log_address

功能：打印参数内容至终端标准输出， 内容前面有提示符`[*] INFO`

参数：

+ `desc(str)`：对address参数的描述
+ `address(int)`：一个整数，打印出来时为16进制

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_address("this is a address",address)
[*] INFO  this is a address ===> 0xdeadbeef
```

### log_address_ex

功能：搜索传入字符串并打印字符串对应变量名和变量值代表的地址内容至终端标准输出

参数：

+ `variable_name(str)`：变量名
+ `depth (int)`：默认是2。若该函数被封装n次，则为2+n

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_address_ex("address")
```

### log_address_ex2

功能：搜索参数并打印参数名和参数值代表的地址内容至终端标准输出

参数：

+ `variable (int)`：变量
+ `depth (int)`：默认是2。若该函数被封装n次，则为2+n

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_address_ex2(address)
[*] INFO  address ===> 0xdeadbeef
```

### log_libc_base_addr

功能：打印`libc`的基地址至终端标准输出

参数：

+ `address(int)`：一个代表libc的基地址的整数

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_libc_base_addr(address)
[*] INFO  libc_base_addr ===> 0xdeadbeef
```

### log_heap_base_addr

功能：打印`heap`的基地址至终端标准输出

参数：

+ `address(int)`：一个代表heap的基地址的整数

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_heap_base_addr(address)
[*] INFO  heap_base_addr ===> 0xdeadbeef
```

### log_code_base_addr

功能：打印程序的基地址至终端标准输出

参数：

+ `address(int)`：一个代表程序基地址的整数

返回值：无

示例：

```text
>>address = 0xdeadbeef
>>log_code_base_addr(address)
[*] INFO  code_base_addr ===> 0xdeadbeef
```

## libc-patch与one_gadget

### ldd_get_libc_path

功能：获得参数对应文件的`libc.so.6`的绝对地址

参数：

+ `filepath(str)`：一个文件路径

返回值：文件所链接的`libc.so.6`的绝对地址

### one_gadget

功能：获得参数对应的`libc.so`的`one_gadget`

参数：

+ `condition(str)`：一个`libc.so`文件的路径或`build-id`
+ `more(bool)`：调整搜索`one_gadget`参数，从而获得更多`one_gadget`

返回值：参数对应的`libc.so`中的`one_gadget`偏移

### one_gadget_binary

功能：获得参数对应的静态链接`elf`文件的`one_gadget`

参数：

+ `binary_path(str)`：`elf`文件路径
+ `more(bool)`：调整搜索`one_gadget`参数，从而获得更多`one_gadget`

返回值：参数对应的静态链接`elf`文件的`one_gadget`偏移

# cli_misc.py

## 常用函数

### get_current_one_gadget_from_file

功能：获得当前运行的文件的`one_gadget`

参数：

+ `libc_base`：使搜索后的`one_gadget`都加上该值
+ `more`：调整搜索`one_gadget`参数，从而获得更多`one_gadget`

返回值：包含当前运行文件的所有`one_gadget`的一个列表

示例：无

### get_current_codebase_addr

功能：获得当前运行文件（进程）的代码段基地址

参数：

+ `use_cache(bool)`：是否使用缓存方便下次读取，默认true

返回值：一个代表代码段基地址的整数

示例：无

### get_current_libcbase_addr

功能：获得当前运行文件（进程）的libc段基地址

参数：

+ `use_cache(bool)`：是否使用缓存方便下次读取，默认true

返回值：一个代表libc段基地址的整数

示例：无

### get_current_stackbase_addr

功能：获得当前运行文件（进程）的栈段基地址

参数：

+ `use_cache(bool)`：是否使用缓存方便下次读取，默认true

返回值：一个代表栈段基地址的整数

示例：无

### get_current_heapbase_addr

功能：获得当前运行文件（进程）的堆段基地址

参数：

+ `use_cache(bool)`：是否使用缓存方便下次读取，默认true

返回值：一个代表堆段基地址的整数

示例：无

## gdb相关

### kill_current_gdb

功能：运行到该函数时关闭`gdb`调试器

参数：

+ 无

返回值：无

示例：无

### execute_cmd_in_current_gdb

功能：运行到该函数时在`gdb`调试器中执行命令

参数：

+ `cmd(str)`：要执行的命令，用"`;`"或者"`\n`"分割多个命令

返回值：无

示例：无

### set_current_pie_breakpoints

功能：运行到该函数时通过传入偏移对开了`pie`的程序下断点（自动加上代码段基地址）

参数：

+ `offset`：要下断点的偏移

返回值：无

示例：无

### tele_current_pie_content

功能：：运行到该函数时查看开了pie的程序的数据

参数：

+ `offset(int)`：要观察的地址
+ `nember(int)`：显示数据的行数

返回值：无

示例：无

## 其他

### recv_current_libc_addr

功能：接收io所代表的进程的数据到`/x7f`或`/xf7`时，根据设置的arch自动将包含"`/x7f`"在内的前3个字节/前6个字节解包为一个整数

参数：

+ `offset(int)`：打包后要减去的整数，默认为0
+ `timeout(int)`：等待时间，默认为5

返回值：一个整数

示例：无


### set_current_libc_base

功能：设置`libc`的基地址，使得`libc.sym.xxx`操作会自动加上基地址

参数：

+ `addr(int)`：获取到的libc地址，默认为0
+ `offset(str or int)`：代表需要减去的值，可为函数名或整数

返回值：一个代表`libc`基地址的整数

示例：无

### set_current_libc_base_and_log

功能：设置`libc`的基地址并打印出该地址，并且使得`libc.sym.xxx`操作会自动加上基地址

参数：

+ `addr(int)`：获取到的`libc`地址
+ `offset(str or int)`：代表需要减去的值，可为函数名或整数

返回值：一个代表`libc`基地址的整数

示例：无

### set_current_code_base

功能：设置`elf`的基地址，使得`elf.sym.xxx`操作会自动加上基地址

参数：

+ `addr(int)`：获取到的`elf`地址
+ `offset(str or int)`：代表需要减去的值，可为函数名或整数

返回值：一个代表`elf`基地址的整数

示例：无

### set_current_code_base_and_log

功能：设置`elf`的基地址并打印出该地址，并且使得`elf.sym.xxx`操作会自动加上基地址

参数：

+ `addr(int)`：获取到的`elf`地址
+ `offset(str or int)`：代表需要减去的值，可为函数名或整数

返回值：一个代表`elf`基地址的整数

示例：无

### set_remote_libc

功能：设置攻击远程需要使用到的`libc`库

参数：

+ `libc_so_patch`：需要设置的`libc`库的路径

返回值：无

示例：无

### copy_current_io

功能：多用于爆破，将当前`io` `fork`，返回一个新的进程号

参数：

+ 无

返回值：新的进程号

示例：

```python
for i in range(0x10):
    try:
        new_func()
    except (EOFError):
        gift.io = copy_current_io()
```

# io_file.py

## io_file_struct

这几个结构体辅助类都支持如下操作：

+ `bytes(obj)`：将结构体打包为字节串
+ `len(obj)`：获取结构体大小
+ `obj.struntil(field_name)`：打包到指定字段为止
+ `Class.show_struct("amd64")`：打印字段偏移

### gconv_step_data_struct

功能：构造 `struct __gconv_step_data`

参数：

+ 无

返回值：`gconv_step_data_struct` 对象

示例：

```python
step_data = gconv_step_data_struct()
step_data.__flags = 1
step_data.__statep = 0xdeadbeef
payload = bytes(step_data)
```

### IO_iconv_t_struct

功能：构造 `struct _IO_iconv_t`

参数：

+ 无

返回值：`IO_iconv_t_struct` 对象

示例：

```python
step_data = gconv_step_data_struct()
step_data.__flags = 1

iconv = IO_iconv_t_struct()
iconv.step = 0xdeadbeef
iconv.step_data = step_data

payload = bytes(iconv)
```

### IO_codecvt_struct

功能：构造 `struct _IO_codecvt`

参数：

+ 无

返回值：`IO_codecvt_struct` 对象

示例：

```python
codecvt = IO_codecvt_struct()
codecvt.__cd_in = IO_iconv_t_struct()
codecvt.__cd_out = IO_iconv_t_struct()

payload = bytes(codecvt)
```

### IO_wide_data_struct

功能：构造 `struct _IO_wide_data`

参数：

+ 无

返回值：`IO_wide_data_struct` 对象

备注：

+ `amd64` 下 `sizeof(struct _IO_wide_data) == 0xe8`
+ `amd64` 下 `_wide_vtable` 偏移为 `0xe0`
+ `_codecvt` 字段可直接赋值为 `IO_codecvt_struct()` 对象

示例：

```python
codecvt = IO_codecvt_struct()
codecvt.__cd_in = IO_iconv_t_struct()

wide_data = IO_wide_data_struct()
wide_data._IO_write_ptr = 1
wide_data._codecvt = codecvt
wide_data._wide_vtable = libc.sym._IO_wfile_jumps

payload = bytes(wide_data)
```

### obstack_chunk_struct

功能：构造 `struct _obstack_chunk`

参数：

+ 无

返回值：`obstack_chunk_struct` 对象

备注：

+ `contents` 对应 chunk 头部之后的可变尾部内容，可直接赋值 `bytes` / `str`
+ `obstack_chunk_struct.sizeof(64)` 返回头部大小 `0x10`
+ `obstack_chunk_struct.sizeof(32)` 返回头部大小 `0x8`
+ `len(obj)` 会把 `contents` 一起算进去，因此通常大于等于 `sizeof(...)`

示例：

```python
chunk = obstack_chunk_struct()
chunk.limit = heap + 0x400
chunk.prev = 0
chunk.contents = b"/bin/sh\x00"

payload = bytes(chunk)
```

### obstack_struct

功能：构造 `struct obstack`

参数：

+ 无

返回值：`obstack_struct` 对象

备注：

+ 常用于 `House of Lys` / `_IO_obstack_jumps` 相关利用
+ 结构体默认跟随当前 `pwntools` 的 `context.bits`
+ `obstack_struct.sizeof(64)` 为 `0x58`
+ `obstack_struct.sizeof(32)` 为 `0x2c`
+ `temp` 同时提供 `tempint` / `tempptr` 两个别名，便于按 union 语义设置
+ `flags` 既可以整体赋值，也可以通过 `use_extra_arg` / `maybe_empty_object` / `alloc_failed` 三个属性按位设置

示例：

```python
context.bits = 64

obstack = obstack_struct()
obstack.chunk_size = 0x100
obstack.chunk = heap + 0x200
obstack.object_base = heap + 0x210
obstack.next_free = heap + 0x218
obstack.chunk_limit = heap + 0x400
obstack.tempptr = heap + 0x300
obstack.alignment_mask = 0xf
obstack.chunkfun = libc.sym.malloc
obstack.freefun = libc.sym.free
obstack.extra_arg = 0
obstack.use_extra_arg = 1
obstack.maybe_empty_object = 1

payload = bytes(obstack)
```

## io_file_attack

### house_of_apple2_execmd_when_exit

功能：生成进行`house of apple2`攻击以便`getshell`的`payload`，详情见：

https://www.roderickchan.cn/post/house-of-apple-%E4%B8%80%E7%A7%8D%E6%96%B0%E7%9A%84glibc%E4%B8%ADio%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95-2/

参数：

+ `standard_FILE_addr(int)`：要确保该参数为`_IO_2_1_stdin_/_IO_2_1_stdout_/_IO_2_1_stderr_`其中一个的地址。若没办法，则该参数-0x30和-0x18处要为0
+ `_IO_wfile_jumps_addr(int)`：`_IO_wfile_jumps_`的地址，一般设为 `libc.sym._IO_wfile_jumps`即可
+ `system_addr(int)`：`system`函数的地址，一般设为`libc.sym.system`
+ `cmd`(str)：要执行的`shell`指令，默认为`sh`

返回值：进行`house of apple2`攻击以便`getshell`的`payload`

示例：无

### house_of_apple2_stack_pivoting_when_exit

功能：生成`house of apple2` 栈迁移攻击的`payload`，详情见：

https://www.roderickchan.cn/post/house-of-apple-%E4%B8%80%E7%A7%8D%E6%96%B0%E7%9A%84glibc%E4%B8%ADio%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95-2/

参数：

+ `standard_FILE_addr(int)`：要确保该参数为`_IO_2_1_stdin_/_IO_2_1_stdout_/_IO_2_1_stderr_`其中一个的地址。若没办法，则该参数-0x30和-0x18处要为0
+ `_IO_wfile_jumps_addr(int)`：`_IO_wfile_jumps_`的地址，一般设为 `libc.sym._IO_wfile_jumps`即可
+ `leave_ret_addr(int)`：代表`leave_ret`汇编指令的地址
+ `pop_rbp_addr(int)`：代表`pop rbp; ret`汇编指令的地址
+ `fake_rbp_addr(int)`：代表要迁移过去的地址 + 8（因为是通过`leave;ret`迁移）

返回值：`house of apple2` 栈迁移攻击的`payload`

示例：

```python
data = IO_FILE_plus_struct().house_of_apple2_stack_pivoting_when_exit(libc.sym._IO_2_1_stderr_,
                                                                      libc.sym._IO_wfile_jumps,
                                                                      libc.search(asm("leave; ret")).__next__(),
                                                                      libc.search(asm("pop rbp; ret")).__next__(),
                                                                      libc.sym._IO_2_1_stderr_ + 0xe0-8)
```



### payload_replace

功能：对数据对应偏移进行替换

参数：

+ `payload(str or bytes)`：要进行替换的数据
+ `rpdict`：用`flat`生成的`payload`

返回值：替换好的数据

示例：

```python
data = IO_FILE_plus_struct().house_of_apple2_stack_pivoting_when_do_IO_operation(
    standard_FILE_addr=libc.sym._IO_2_1_stdout_,
    _IO_wfile_jumps_addr=libc.sym._IO_wfile_jumps,
    leave_ret_addr=lbs + 0x000000000004ae07,
    pop_rbp_addr=lbs + 0x0000000000023730,
    fake_rbp_addr=0xdeadbeef
)

data = payload_replace(data, {
    0x38: 0x7ffff7f957b0,
    0x10: mov_rdx2rsp,
    0x68: lbs + 0x00000000000f5d27
})
```

# ld_so.py

## ld_so_struct

这些结构体辅助类主要用于 `House of Banana` 一类和 `ld.so` / `link_map` 相关的利用。

共同支持：

+ `bytes(obj)`：将结构体打包为字节串
+ `len(obj)`：获取当前结构体大小
+ `obj.struntil(field_name)`：打包到指定字段为止
+ `Class.show_struct("amd64")`：打印关键字段偏移
+ `Class.sizeof(64)` / `Class.sizeof(32)`：不依赖当前 `context.bits`，直接查询对应位数下的结构体大小

备注：

+ 这些结构体默认跟随当前 `pwntools` 的 `context.bits`
+ 直接 `from pwncli import *` 之后，默认一般是 `i386/32-bit`
+ 所以如果你要 `amd64` 结果，需要先 `context.bits = 64` 或 `context.arch = "amd64"`
+ `link_namespace_struct` 只实现 `_rtld_global._dl_ns[i]` 的常用前缀
+ `link_namespaces_struct` 实现单个 `_dl_ns[i]` 的完整布局（面向 glibc 2.32 / amd64,i386）
+ `link_map_struct` 这里实现的是 `House of Banana` 常用的前缀部分，重点包含 `l_info`
+ `rtld_global_struct` 实现的是到 `_dl_rtld_map` 为止的常用前缀，便于直接伪造 `_rtld_global`
+ 更深层、版本差异较大的尾部成员可以通过 `suffix` 或 `payload_replace` 继续扩展

示例：

```python
from pwncli import *

hex(len(rtld_global_struct()))
# 默认通常是 0x6fc，因为 context.bits == 32

context.bits = 64
hex(len(rtld_global_struct()))
# 0xce0

hex(rtld_global_struct.sizeof(64))
# 0xce0
```

### Elf_Dyn_struct

功能：构造 `ElfW(Dyn)` 结构体

参数：

+ 无

返回值：`Elf_Dyn_struct` 对象

示例：

```python
dyn = Elf_Dyn_struct()
dyn.d_tag = DT_FINI_ARRAY
dyn.d_ptr = heap + 0x400
payload = bytes(dyn)
```

### link_namespace_struct

功能：构造 `_rtld_global._dl_ns[i]` 中常用的前缀部分

参数：

+ 无

返回值：`link_namespace_struct` 对象

示例：

```python
ns = link_namespace_struct()
ns._ns_loaded = heap
ns._ns_nloaded = 1
payload = bytes(ns)
```

### link_namespaces_struct

功能：构造单个 `_rtld_global._dl_ns[i]` 的完整结构

参数：

+ 无

返回值：`link_namespaces_struct` 对象

备注：

+ `len(link_namespaces_struct())` 在 `amd64` 下是 `0x98`
+ 包含 `_ns_unique_sym_table` 和 `_ns_debug`
+ 如果只关心 `_ns_loaded` / `libc_map` 等前缀字段，仍然可以继续用 `link_namespace_struct`

示例：

```python
ns = link_namespaces_struct()
ns._ns_loaded = fake_link_map
ns._ns_nloaded = 1
ns.libc_map = fake_libc_map

payload = bytes(ns)
```

### link_map_struct

功能：构造 `struct link_map` 的 `House of Banana` 常用前缀

参数：

+ 无

返回值：`link_map_struct` 对象

备注：

+ `l_info` 一共有 `80` 项，可直接赋值为列表
+ 提供 `set_l_info()` / `get_l_info()` 方便设置单个索引
+ 提供 `l_info_dt_fini` / `l_info_dt_fini_array` / `l_info_dt_fini_arraysz` 三个常用别名
+ `amd64` 下 `l_info[DT_FINI_ARRAY]` 偏移是 `0x110`
+ `amd64` 下 `l_info[DT_FINI_ARRAYSZ]` 偏移是 `0x120`

示例：

```python
lm = link_map_struct()
lm.l_addr = 0
lm.l_next = 0
lm.l_real = fake_link_map_addr
lm.l_info_dt_fini_array = fake_link_map_addr + 0x110
lm.l_info_dt_fini_arraysz = fake_link_map_addr + 0x120

payload = bytes(lm)
```

### rtld_global_struct

功能：构造 `_rtld_global` 的 `House of Banana` 常用前缀

参数：

+ 无

返回值：`rtld_global_struct` 对象

备注：

+ 当前实现覆盖 `_dl_ns[DL_NNS]` 到 `_dl_rtld_map` 这一段
+ `amd64` 下 `rtld_global_struct.dl_nns_offset()` 是 `0x980`
+ `amd64` 下 `rtld_global_struct.dl_rtld_map_offset()` 是 `0xa08`
+ `set_dl_ns()` 支持按索引替换单个 namespace
+ `_dl_ns` 中既可以放完整的 `link_namespaces_struct`，也可以放更短的 `link_namespace_struct` 前缀，打包时会按真实 stride 自动补零
+ `len(rtld_global_struct())` 返回当前实现的前缀长度；如果要继续拼更深层尾部，可以写到 `suffix`

示例：

```python
ns0 = link_namespace_struct()
ns0._ns_loaded = fake_link_map
ns0._ns_nloaded = 1

rtld = rtld_global_struct()
rtld.set_dl_ns(0, ns0)
rtld._dl_nns = 1

payload = bytes(rtld)
```
