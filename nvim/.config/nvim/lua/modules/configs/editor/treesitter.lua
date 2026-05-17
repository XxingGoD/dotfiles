local function get_lang(bufnr)
	local filetype = vim.bo[bufnr].filetype
	if filetype == "" then
		return nil
	end

	return vim.treesitter.language.get_lang(filetype)
end

local function has_parser(lang)
	if not lang then
		return false
	end

	local ok, loaded = pcall(vim.treesitter.language.add, lang)
	return ok and loaded == true
end

local function disable_auto_indent(bufnr)
	vim.bo[bufnr].autoindent = false
	vim.bo[bufnr].smartindent = false
	vim.bo[bufnr].copyindent = false
	vim.bo[bufnr].preserveindent = false
	vim.bo[bufnr].cindent = false
	vim.bo[bufnr].indentexpr = ""
end

local function start_treesitter(bufnr)
	local lang = get_lang(bufnr)
	if not has_parser(lang) then
		return nil
	end

	pcall(vim.treesitter.start, bufnr, lang)
	return lang
end

local function enable_treesitter_folds(bufnr)
	local lang = start_treesitter(bufnr)
	if not lang then
		vim.wo.foldmethod = "manual"
		vim.wo.foldexpr = "0"
		return
	end

	if vim.treesitter.query.get(lang, "folds") then
		vim.wo.foldmethod = "expr"
		vim.wo.foldexpr = "v:lua.vim.treesitter.foldexpr()"
	else
		vim.wo.foldmethod = "manual"
		vim.wo.foldexpr = "0"
	end
end

return function()
	require("modules.utils").load_plugin("nvim-treesitter", {})

	local group = vim.api.nvim_create_augroup("nvimdots_treesitter", { clear = true })

	vim.api.nvim_create_autocmd("FileType", {
		group = group,
		callback = function(event)
			disable_auto_indent(event.buf)
			enable_treesitter_folds(event.buf)
		end,
	})

	vim.api.nvim_create_autocmd("BufWinEnter", {
		group = group,
		callback = function(event)
			if vim.bo[event.buf].filetype ~= "" then
				disable_auto_indent(event.buf)
				enable_treesitter_folds(event.buf)
			end
		end,
	})

	require("nvim-treesitter").install(require("core.settings").treesitter_deps)
end
