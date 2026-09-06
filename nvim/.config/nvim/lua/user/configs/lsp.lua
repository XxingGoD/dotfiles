local clice_config = vim.lsp.config.clice or {}
local capabilities = require("cmp_nvim_lsp").default_capabilities(vim.lsp.protocol.make_client_capabilities())
capabilities = vim.tbl_deep_extend("force", capabilities, clice_config.capabilities or {})

local function has_compile_commands(dir)
	local candidates = {
		dir,
		dir .. "/build",
		dir .. "/cmake-build-debug",
		dir .. "/cmake-build-release",
		dir .. "/cmake-build-relwithdebinfo",
		dir .. "/cmake-build-minsizerel",
		dir .. "/out/build",
	}

	for _, candidate in ipairs(candidates) do
		if vim.uv.fs_stat(candidate .. "/compile_commands.json") then
			return true
		end
	end

	return false
end

local function find_root(bufnr)
	local fname = vim.api.nvim_buf_get_name(bufnr)
	local home = vim.fs.normalize(vim.uv.os_homedir())
	if fname ~= "" then
		for dir in vim.fs.parents(fname) do
			if vim.fs.normalize(dir) == home then
				break
			end
			if has_compile_commands(dir) then
				return dir
			end
		end
	end

	local root = vim.fs.root(bufnr, clice_config.root_markers or {})
	if root and vim.fs.normalize(root) ~= home then
		return root
	end

	local file_dir = fname ~= "" and vim.fs.normalize(vim.fs.dirname(fname)) or nil
	return file_dir ~= home and file_dir or nil
end

vim.lsp.enable("clangd", false)
vim.lsp.config("clice", {
	capabilities = capabilities,
	root_dir = function(bufnr, on_dir)
		if vim.b[bufnr].bigfile == true or vim.b[bufnr].large_file == true then
			return
		end

		on_dir(find_root(bufnr))
	end,
})
vim.lsp.enable("clice")
