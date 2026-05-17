-- https://github.com/neovim/nvim-lspconfig/blob/master/lsp/ruff.lua
return {
	cmd = { "ruff", "server" },
	filetypes = { "python" },
	root_markers = { "pyproject.toml", "ruff.toml", ".ruff.toml", ".git" },
	init_options = {
		settings = {
			configuration = {
				lint = {
					["per-file-ignores"] = {
						["**/exp*.py"] = { "E731" },
						["**/*pwn*.py"] = { "E731" },
					},
				},
			},
			lint = {
				select = {
					-- enable: pycodestyle
					"E",
					-- enable: pyflakes
					"F",
				},
				extendSelect = {
					-- enable: isort
					"I",
				},
				ignore = {
					-- ignore wildcard-import diagnostics
					"F403",
					"F405",
				},
			},
			-- the same line length as black
			lineLength = 88,
			configurationPreference = "filesystemFirst",
		},
	},
}
