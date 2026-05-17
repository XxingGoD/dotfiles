-- https://detachhead.github.io/basedpyright
local pwncli_source_root = "/home/starlight/CtfTools/pwncli"

return {
	settings = {
		basedpyright = {
			disableOrganizeImports = true,
			analysis = {
				autoSearchPaths = true,
				extraPaths = vim.fn.isdirectory(pwncli_source_root) == 1 and { pwncli_source_root } or {},
				diagnosticMode = "openFilesOnly",
				typeCheckingMode = "standard",
				diagnosticSeverityOverrides = {
					-- pwntools exploit scripts commonly use `from pwn import *`
					-- and small helpers like `debug(...)`, which clash with
					-- names exported by the library and create noisy false positives.
					reportAssignmentType = "none",
					reportWildcardImportFromLibrary = "none",
				},
				exclude = {
					"**/.venv",
					"**/venv",
					"**/env",
					"**/__pycache__",
					"**/site-packages",
					"**/dist-packages",
					"**/PwnVenv",
				},
				ignore = {
					"**/.venv",
					"**/venv",
					"**/env",
					"**/site-packages",
					"**/dist-packages",
					"**/PwnVenv",
				},
			},
		},
	},
}
