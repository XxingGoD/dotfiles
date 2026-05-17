if status is-interactive
    # Commands to run in interactive sessions can go here
end
set fish_greeting ""
set -p PATH ~/.local/bin
starship init fish | source
zoxide init fish --cmd cd | source
set -p PATH $HOME/.npm-global/bin
set -p PATH $HOME/CtfTools/scripts/
set -p PATH $HOME/CtfTools/libc-database/
set -gx PATH $HOME/go/bin $PATH

# source ~/CtfTools/PwnVenv/bin/activate.fish

# Keep IDA available after virtualenv activation adjusts PATH.
set -gx IDA_HOME $HOME/CtfTools/IDA9.2
if not contains -- $IDA_HOME $PATH
    fish_add_path -g $IDA_HOME
end

function y
	set tmp (mktemp -t "yazi-cwd.XXXXXX")
	yazi $argv --cwd-file="$tmp"
	if read -z cwd < "$tmp"; and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
		builtin cd -- "$cwd"
	end
	rm -f -- "$tmp"
end

function cat 
	command bat $argv
end
function ls
	command eza --icons $argv
end

function lt
	command eza --icons --tree $argv
end
# grub
abbr grub 'LANGUAGE=en_US.UTF-8 LANG=en_US.UTF-8 sudo grub-mkconfig -o /boot/grub/grub.cfg'

abbr lsfg 'LSFG_PROCESS="miyu"'
# fa运行fastfetch
abbr fa fastfetch
abbr reboot 'systemctl reboot'
function sl 
	command sl | lolcat	
end
function 滚
	sysup 
end
function raw
	command ~/.local/bin/random-anime-wallpaper-dms $argv
end

function 安装
	command yay -S $argv
end

function 卸载
	command yay -Rns $argv
end 



# pnpm
set -gx PNPM_HOME "/home/starlight/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end

set -gx C_INCLUDE_PATH /home/starlight/XG/PWN/kernel $C_INCLUDE_PATH

set -gx MANPAGER 'less -R'
set -gx GROFF_NO_SGR 1

set -gx LESS_TERMCAP_mb (printf '\e[1;31m')
set -gx LESS_TERMCAP_md (printf '\e[1;36m')
set -gx LESS_TERMCAP_me (printf '\e[0m')
set -gx LESS_TERMCAP_se (printf '\e[0m')
set -gx LESS_TERMCAP_so (printf '\e[1;44;33m')
set -gx LESS_TERMCAP_ue (printf '\e[0m')
set -gx LESS_TERMCAP_us (printf '\e[1;32m')
