-- https://detachhead.github.io/basedpyright
local pwncli_source_root = "/home/starlight/CtfTools/pwncli"
local python_root_markers = {
	"pyrightconfig.json",
	"pyproject.toml",
	"setup.py",
	"setup.cfg",
	"requirements.txt",
	"Pipfile",
}

local function find_python_root(bufnr)
	local fname = vim.api.nvim_buf_get_name(bufnr)
	if fname == "" then
		return nil
	end

	local marker = vim.fs.find(python_root_markers, {
		path = fname,
		upward = true,
	})[1]
	if not marker then
		return nil
	end

	local root = vim.fs.normalize(vim.fs.dirname(marker))
	-- Treating $HOME as a Python workspace makes basedpyright enumerate the
	-- entire home directory, which is too expensive on this machine.
	if root == vim.fs.normalize(vim.uv.os_homedir()) then
		return nil
	end

	return root
end

return {
	root_dir = function(bufnr, on_dir)
		on_dir(find_python_root(bufnr))
	end,
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
