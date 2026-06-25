if status is-interactive
    # Commands to run in interactive sessions can go here
end
set fish_greeting ""
set -p PATH ~/.local/bin
starship init fish | source

set -g STARSHIP_CONFIG_MAIN $HOME/dotfiles/starship/.config/starship.toml
set -g STARSHIP_CONFIG_LITE $HOME/dotfiles/starship/.config/starship-lite.toml

function __starlight_starship_config
    if string match -q -- "$HOME/CODE/OS-Course-Lab" "$PWD"; or string match -q -- "$HOME/CODE/OS-Course-Lab/*" "$PWD"
        echo $STARSHIP_CONFIG_LITE
    else
        echo $STARSHIP_CONFIG_MAIN
    end
end

function fish_prompt
    switch "$fish_key_bindings"
        case fish_hybrid_key_bindings fish_vi_key_bindings fish_helix_key_bindings
            set STARSHIP_KEYMAP "$fish_bind_mode"
        case '*'
            set STARSHIP_KEYMAP insert
    end

    set STARSHIP_CMD_PIPESTATUS $pipestatus
    set STARSHIP_CMD_STATUS $status
    set STARSHIP_DURATION "$CMD_DURATION$cmd_duration"

    __starship_set_job_count

    set -l starship_config (__starlight_starship_config)

    if contains -- --final-rendering $argv; or test "$TRANSIENT" = "1"
        if test "$TRANSIENT" = "1"
            set -g TRANSIENT 0
            printf \e\[0J
        end
        if type -q starship_transient_prompt_func
            starship_transient_prompt_func --terminal-width="$COLUMNS" --status=$STARSHIP_CMD_STATUS --pipestatus="$STARSHIP_CMD_PIPESTATUS" --keymap=$STARSHIP_KEYMAP --cmd-duration=$STARSHIP_DURATION --jobs=$STARSHIP_JOBS
        else
            printf "\e[1;32m❯\e[0m "
        end
    else
        env STARSHIP_CONFIG="$starship_config" /usr/bin/starship prompt --terminal-width="$COLUMNS" --status=$STARSHIP_CMD_STATUS --pipestatus="$STARSHIP_CMD_PIPESTATUS" --keymap=$STARSHIP_KEYMAP --cmd-duration=$STARSHIP_DURATION --jobs=$STARSHIP_JOBS
    end
end

function fish_right_prompt
    switch "$fish_key_bindings"
        case fish_hybrid_key_bindings fish_vi_key_bindings fish_helix_keybindings
            set STARSHIP_KEYMAP "$fish_bind_mode"
        case '*'
            set STARSHIP_KEYMAP insert
    end

    set STARSHIP_CMD_PIPESTATUS $pipestatus
    set STARSHIP_CMD_STATUS $status
    set STARSHIP_DURATION "$CMD_DURATION$cmd_duration"

    __starship_set_job_count

    set -l starship_config (__starlight_starship_config)

    if contains -- --final-rendering $argv; or test "$RIGHT_TRANSIENT" = "1"
        set -g RIGHT_TRANSIENT 0
        if type -q starship_transient_rprompt_func
            starship_transient_rprompt_func --terminal-width="$COLUMNS" --status=$STARSHIP_CMD_STATUS --pipestatus="$STARSHIP_CMD_PIPESTATUS" --keymap=$STARSHIP_KEYMAP --cmd-duration=$STARSHIP_DURATION --jobs=$STARSHIP_JOBS
        else
            printf ""
        end
    else
        env STARSHIP_CONFIG="$starship_config" /usr/bin/starship prompt --right --terminal-width="$COLUMNS" --status=$STARSHIP_CMD_STATUS --pipestatus="$STARSHIP_CMD_PIPESTATUS" --keymap=$STARSHIP_KEYMAP --cmd-duration=$STARSHIP_DURATION --jobs=$STARSHIP_JOBS
    end
end

zoxide init fish --cmd cd | source
direnv hook fish | source
set -p PATH $HOME/.npm-global/bin
set -gx PATH $HOME/.cargo/bin $PATH
set -p PATH $HOME/CtfTools/scripts/
set -p PATH $HOME/CtfTools/libc-database/
set -gx PATH $HOME/go/bin $PATH
set -g fish_key_bindings fish_vi_key_bindings
set -p PATH $HOME/.dotnet/tools $PATH
# source ~/CtfTools/PwnVenv/bin/activate.fish

# Keep IDA available after virtualenv activation adjusts PATH.
set -gx IDA_HOME $HOME/CtfTools/IDA9.4
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

set -gx PAGER 'less -R'
set -gx LESS '-R'
set -gx MANPAGER 'less -R'
set -gx GROFF_NO_SGR 1

set -gx LESS_TERMCAP_mb (printf '\e[1;31m')
set -gx LESS_TERMCAP_md (printf '\e[1;36m')
set -gx LESS_TERMCAP_me (printf '\e[0m')
set -gx LESS_TERMCAP_se (printf '\e[0m')
set -gx LESS_TERMCAP_so (printf '\e[1;44;33m')
set -gx LESS_TERMCAP_ue (printf '\e[0m')
set -gx LESS_TERMCAP_us (printf '\e[1;32m')


# BEGIN opam configuration
# This is useful if you're using opam as it adds:
#   - the correct directories to the PATH
#   - auto-completion for the opam binary
# This section can be safely removed at any time if needed.
test -r '/home/starlight/.opam/opam-init/init.fish' && source '/home/starlight/.opam/opam-init/init.fish' > /dev/null 2> /dev/null; or true
# END opam configuration
