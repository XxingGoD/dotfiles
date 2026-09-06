-- Official clice config for Neovim 0.11 and newer.
return {
	filetypes = { "c", "cpp" },

	root_markers = {
		".git/",
		"clice.toml",
		".clang-tidy",
		".clang-format",
		"compile_commands.json",
		"compile_flags.txt",
		"configure.ac",
	},

	capabilities = {
		textDocument = {
			completion = {
				editsNearCursor = true,
			},
		},
		offsetEncoding = { "utf-8" },
	},

	cmd = { "clice", "serve" },
}
