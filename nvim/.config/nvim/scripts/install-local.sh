#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}/nvim"
INSTALL_MODE="copy"
BOOTSTRAP=1
UPDATE_SHELL=1

usage() {
	cat <<'EOF'
Install the current Neovim config to ~/.config/nvim in one step.

Usage:
  bash scripts/install-local.sh [options]

Options:
  --target DIR      Install to a custom target directory
  --link            Symlink the config instead of copying it
  --copy            Copy the config (default)
  --no-bootstrap    Skip the headless Neovim bootstrap step
  --no-shell        Skip adding Mason's bin directory to your shell PATH
  -h, --help        Show this help text
EOF
}

log() {
	printf '[nvim-install] %s\n' "$*"
}

warn() {
	printf '[nvim-install] warning: %s\n' "$*" >&2
}

die() {
	printf '[nvim-install] error: %s\n' "$*" >&2
	exit 1
}

canonical_path() {
	local path="$1"
	if [ -e "$path" ] || [ -L "$path" ]; then
		readlink -f "$path"
	else
		printf '%s\n' "$path"
	fi
}

same_path() {
	[ "$(canonical_path "$1")" = "$(canonical_path "$2")" ]
}

backup_existing_target() {
	local backup_dir

	if [ ! -e "$TARGET_DIR" ] && [ ! -L "$TARGET_DIR" ]; then
		return 0
	fi

	if same_path "$SOURCE_DIR" "$TARGET_DIR"; then
		log "Target already points to this config: $TARGET_DIR"
		return 0
	fi

	backup_dir="${TARGET_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
	log "Backing up existing config to $backup_dir"
	mv "$TARGET_DIR" "$backup_dir"
}

install_config() {
	mkdir -p "$(dirname "$TARGET_DIR")"

	if same_path "$SOURCE_DIR" "$TARGET_DIR"; then
		log "Skipping file install because source and target are the same"
		return 0
	fi

	case "$INSTALL_MODE" in
	copy)
		log "Copying config to $TARGET_DIR"
		mkdir -p "$TARGET_DIR"
		cp -a "$SOURCE_DIR"/. "$TARGET_DIR"/
		;;
	link)
		log "Linking config to $TARGET_DIR"
		ln -s "$SOURCE_DIR" "$TARGET_DIR"
		;;
	*)
		die "Unknown install mode: $INSTALL_MODE"
		;;
	esac
}

append_block_if_missing() {
	local file="$1"
	local begin_marker="$2"
	local end_marker="$3"
	local block="$4"

	mkdir -p "$(dirname "$file")"
	touch "$file"

	if grep -Fq "$begin_marker" "$file"; then
		return 0
	fi

	printf '\n%s\n%s\n%s\n' "$begin_marker" "$block" "$end_marker" >>"$file"
}

update_shell_path() {
	local current_shell rc_file
	current_shell="$(basename "${SHELL:-bash}")"

	case "$current_shell" in
	bash)
		rc_file="${HOME}/.bashrc"
		append_block_if_missing \
			"$rc_file" \
			"# >>> nvim mason path >>>" \
			"# <<< nvim mason path <<<" \
			'export PATH="$HOME/.local/share/nvim/mason/bin:$PATH"'
		log "Updated $rc_file"
		;;
	zsh)
		rc_file="${HOME}/.zshrc"
		append_block_if_missing \
			"$rc_file" \
			"# >>> nvim mason path >>>" \
			"# <<< nvim mason path <<<" \
			'export PATH="$HOME/.local/share/nvim/mason/bin:$PATH"'
		log "Updated $rc_file"
		;;
	fish)
		rc_file="${HOME}/.config/fish/config.fish"
		append_block_if_missing \
			"$rc_file" \
			"# >>> nvim mason path >>>" \
			"# <<< nvim mason path <<<" \
			'fish_add_path -a $HOME/.local/share/nvim/mason/bin'
		log "Updated $rc_file"
		;;
	*)
		warn "Unsupported shell '$current_shell'; skipping PATH update"
		;;
	esac
}

check_optional_tools() {
	local missing=()
	local tool

	for tool in git rg fd node python3 cargo rustup gcc make; do
		if ! command -v "$tool" >/dev/null 2>&1; then
			missing+=("$tool")
		fi
	done

	if [ "${#missing[@]}" -gt 0 ]; then
		warn "Optional tools missing: ${missing[*]}"
		warn "The config can still install, but some plugins or language tooling may be limited."
	fi
}

bootstrap_nvim() {
	if ! command -v nvim >/dev/null 2>&1; then
		warn "Neovim is not installed; skipping bootstrap"
		return 0
	fi

	if ! command -v git >/dev/null 2>&1; then
		warn "Git is not installed; skipping bootstrap"
		return 0
	fi

	if [ "$TARGET_DIR" != "${XDG_CONFIG_HOME:-${HOME}/.config}/nvim" ] && ! same_path "$TARGET_DIR" "${XDG_CONFIG_HOME:-${HOME}/.config}/nvim"; then
		warn "Custom target detected; skipping bootstrap because Neovim will not load it by default."
		warn "Run with XDG_CONFIG_HOME or move the config to ~/.config/nvim before bootstrapping."
		return 0
	fi

	log "Bootstrapping plugins with headless Neovim"
	nvim --headless "+Lazy! sync" "+qa"
}

while [ "$#" -gt 0 ]; do
	case "$1" in
	--target)
		[ "$#" -ge 2 ] || die "--target requires a directory"
		TARGET_DIR="$2"
		shift 2
		;;
	--link)
		INSTALL_MODE="link"
		shift
		;;
	--copy)
		INSTALL_MODE="copy"
		shift
		;;
	--no-bootstrap)
		BOOTSTRAP=0
		shift
		;;
	--no-shell)
		UPDATE_SHELL=0
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		die "Unknown argument: $1"
		;;
	esac
done

check_optional_tools
backup_existing_target
install_config

if [ "$UPDATE_SHELL" -eq 1 ]; then
	update_shell_path
fi

if [ "$BOOTSTRAP" -eq 1 ]; then
	bootstrap_nvim
fi

log "Install finished"
