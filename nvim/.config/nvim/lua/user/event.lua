local definitions = {
	-- Example
	bufs = {
		{ "BufWritePre", "COMMIT_EDITMSG", "setlocal noundofile" },
	},
	neovide = {
		{ "VimEnter,ColorScheme", "*", "lua require('user.neovide').apply()" },
	},
}

return definitions
