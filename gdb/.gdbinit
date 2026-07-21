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

set print pretty on
set print object on
set print static-members on
set print vtbl on
