local function path_exists(path)
	return vim.uv.fs_stat(path) ~= nil
end

local home = vim.env.HOME or vim.fn.expand("~")
local pwn_python = vim.fs.joinpath(home, "CtfTools", "PwnVenv", "bin", "python")
local pwncli_root = vim.fs.joinpath(home, "CtfTools", "pwncli")

local analysis = {
	autoSearchPaths = true,
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
}

if path_exists(pwncli_root) then
	analysis.extraPaths = { pwncli_root }
end

local python = {}
if path_exists(pwn_python) then
	python.pythonPath = pwn_python
end

return {
	settings = {
		python = python,
		basedpyright = {
			disableOrganizeImports = true,
			analysis = analysis,
		},
	},
}
