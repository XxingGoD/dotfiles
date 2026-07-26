source /usr/share/pwndbg/gdbinit.py
source /home/starlight/CtfTools/vheap/vheap.py
source /usr/share/pwngdb/pwngdb.py
source /usr/share/pwngdb/angelheap/gdbinit.py
source /home/starlight/splitmind/gdbinit.py
source /home/starlight/CtfTools/ret-sync/ext_gdb/sync.py

define hook-run
python
import angelheap
angelheap.init_angelheap()
end
end

set debuginfod enabled off
set pagination off
set confirm off


define add-kmod
    set $modname = $arg0
    set $text_addr = $arg1
    add-symbol-file $modname.ko -s .text $text_addr
end

set context-clear-screen off

python

# 默认使用模式
default_mode = "m"

class SwitchModeCommand(gdb.Command):
    """Custom command to switch display mode"""
    
    def __init__(self):
        super(SwitchModeCommand, self).__init__("switch-mode", gdb.COMMAND_USER)
        self.current_splitter = None
    
    def invoke(self, arg, from_tty):
        if not arg:
            print("Usage: switch-mode [s|d|m]")
            print("  s - source code")
            print("  d - disasm")  
            print("  m - mixed")
            return
            
        mode = arg.strip().lower()
        if mode not in ['s', 'd', 'm']:
            print("Invalid mode. Use s, d, or m")
            return
            
        self.setup_layout(mode)
        print(f"Switched to mode: {mode}")
    
    def setup_layout(self, mode):
        # 清理现有布局
        if self.current_splitter is not None:
            try:
                self.current_splitter.close()
            except:
                # 如果清理失败，可能是因为窗格已被删除，忽略错误
                pass
        
        # 重新设置布局
        import splitmind
        spliter = splitmind.Mind()
        self.current_splitter = spliter.splitter
        
        spliter.select("main").right(display="regs", size="50%")
        
        sections = "regs"
        gdb.execute("set context-stack-lines 10")
        
        legend_on = "code"
        if mode == "d":
            legend_on = "disasm"
            sections += " disasm"
            spliter.select("main").above(display="disasm", size="70%", banner="none")
            # 设置反汇编上下文行数
            gdb.execute("set context-disasm-lines 25")
        elif mode == "s":
            sections += " code"
            spliter.select("main").above(display="code", size="70%", banner="none")
            # 设置源码上下文行数
            gdb.execute("set context-code-lines 30")
        else:
            sections += " disasm code"
            spliter.select("main").above(display="code", size="70%", banner="none")
            spliter.select("code").below(display="disasm", size="40%", banner="none")
            gdb.execute("set context-code-lines 25")
            gdb.execute("set context-disasm-lines 10")
        
        sections += " args stack backtrace expressions"
        
        spliter.show("legend", on=legend_on)
        # 布局右边窗口
        spliter.show("stack", on="regs")
        spliter.show("backtrace", on="regs")
        spliter.show("args", on="regs")
        spliter.show("expressions", on="args")
        # 基本的pwndbg配置
        gdb.execute("set context-sections %s" % sections)
        # 设置栈帧显示行数
        gdb.execute("set context-stack-lines 20")
        # 显示返回地址寄存器
        gdb.execute("set show-retaddr-reg on")
        # 设置代码缩进
        gdb.execute("set context-code-tabstop 4")
        spliter.build()

# 注册命令
SwitchModeCommand()

# 使用默认模式初始化
cmd = SwitchModeCommand()
cmd.setup_layout(default_mode)

print("GDB layout initialized with default mode. Use 'switch-mode [s|d|m]' to change.")

end

set print pretty on
set print object on
set print static-members on
set print vtbl on
