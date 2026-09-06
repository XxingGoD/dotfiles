local bind = require("keymap.bind")
local map_cr = bind.map_cr
local map_callback = bind.map_callback
local helpers = require("keymap.helpers")

---@param buf integer
---@return vim.lsp.Client[]
local function get_buf_clients(buf)
	return vim.lsp.get_clients({ bufnr = buf })
end

---@param buf integer
local function start_buf_lsp(buf)
	local ok, err = pcall(vim.api.nvim_exec_autocmds, "FileType", {
		group = "nvim.lsp.enable",
		buffer = buf,
		modeline = false,
	})
	if not ok then
		vim.notify(err, vim.log.levels.ERROR, { title = "LSP Start" })
	end
end

---@param buf integer
local function stop_buf_lsp(buf)
	local clients = get_buf_clients(buf)
	if vim.tbl_isempty(clients) then
		vim.notify("No LSP clients attached to this buffer", vim.log.levels.INFO, { title = "LSP Stop" })
		return
	end

	for _, client in ipairs(clients) do
		client:stop()
	end
end

---@param buf integer
local function restart_buf_lsp(buf)
	local clients = get_buf_clients(buf)
	if vim.tbl_isempty(clients) then
		start_buf_lsp(buf)
		return
	end

	for _, client in ipairs(clients) do
		client:stop(true)
	end

	vim.defer_fn(function()
		if vim.api.nvim_buf_is_valid(buf) then
			start_buf_lsp(buf)
		end
	end, 100)
end

---@param buf integer
local function show_buf_lsp_info(buf)
	local clients = get_buf_clients(buf)
	if vim.tbl_isempty(clients) then
		vim.notify("No LSP clients attached to this buffer", vim.log.levels.INFO, { title = "LSP Info" })
		return
	end

	local lines = {}
	for _, client in ipairs(clients) do
		lines[#lines + 1] = string.format(
			"%s (id=%d)%s",
			client.name,
			client.id,
			client.root_dir and (" [" .. client.root_dir .. "]") or ""
		)
	end

	vim.notify(table.concat(lines, "\n"), vim.log.levels.INFO, { title = "LSP Info" })
end

local mappings = {
	fmt = {
		["n|<A-f>"] = map_cr("FormatToggle"):with_noremap():with_silent():with_desc("formatter: Toggle format on save"),
		["n|<A-S-f>"] = map_cr("Format"):with_noremap():with_silent():with_desc("formatter: Format buffer manually"),
	},
}
bind.nvim_load_mapping(mappings.fmt)

--- The following code allows this file to be exported ---
---    for use with LSP lazy-loaded keymap bindings    ---

local M = {}

---@param buf integer
function M.lsp(buf)
	local map = {
		-- LSP-related keymaps, ONLY effective in buffers with LSP(s) attached
		["n|<leader>li"] = map_callback(function()
				show_buf_lsp_info(buf)
			end)
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Info"),
		["n|<leader>lr"] = map_callback(function()
				restart_buf_lsp(buf)
			end)
			:with_silent()
			:with_buffer(buf)
			:with_nowait()
			:with_desc("lsp: Restart"),
		["n|<leader>ls"] = map_callback(function()
				stop_buf_lsp(buf)
			end)
			:with_silent()
			:with_buffer(buf)
			:with_nowait()
			:with_desc("lsp: Stop"),
		["n|<leader>lS"] = map_callback(function()
				start_buf_lsp(buf)
			end)
			:with_silent()
			:with_buffer(buf)
			:with_nowait()
			:with_desc("lsp: Start"),
		["n|<leader>so"] = map_cr("Trouble symbols toggle win.position=right")
			:with_silent()
			:with_buffer(buf)
			:with_desc("symbols: Toggle outline"),
		["n|<leader>st"] = map_callback(function()
				helpers.picker("lsp_document_symbols")
			end)
			:with_silent()
			:with_buffer(buf)
			:with_desc("symbols: Document symbols"),
		["n|<leader>sw"] = map_callback(function()
				helpers.picker("lsp_workspace_symbols")
			end)
			:with_silent()
			:with_buffer(buf)
			:with_desc("symbols: Workspace symbols"),
		["n|<leader>sp"] = map_cr("Lspsaga peek_definition")
			:with_silent()
			:with_buffer(buf)
			:with_desc("symbols: Preview definition"),
		["n|go"] = map_cr("Trouble symbols toggle win.position=right")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Toggle outline"),
		["n|gto"] = map_callback(function()
				helpers.picker("lsp_document_symbols")
			end)
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Toggle outline in Telescope"),
		["n|g["] = map_cr("Lspsaga diagnostic_jump_prev")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Prev diagnostic"),
		["n|g]"] = map_cr("Lspsaga diagnostic_jump_next")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Next diagnostic"),
		["n|<leader>lx"] = map_cr("Lspsaga show_line_diagnostics ++unfocus")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Line diagnostic"),
		["n|gs"] = map_callback(function()
			vim.lsp.buf.signature_help()
		end):with_buffer(buf):with_desc("lsp: Signature help"),
		["n|grn"] = map_cr("Lspsaga rename")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Rename in file range"),
		["n|<F2>"] = map_cr("Lspsaga rename")
			:with_silent()
			:with_nowait()
			:with_buffer(buf)
			:with_desc("lsp: Rename"),
		["n|gR"] = map_cr("Lspsaga rename ++project")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Rename in project range"),
		["n|K"] = map_cr("Lspsaga hover_doc"):with_silent():with_buffer(buf):with_desc("lsp: Show doc"),
		["nv|ga"] = map_cr("Lspsaga code_action")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Code action for cursor"),
		["n|gd"] = map_cr("Lspsaga peek_definition")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Preview definition"),
		["n|gD"] = map_cr("Lspsaga goto_definition"):with_silent():with_buffer(buf):with_desc("lsp: Goto definition"),
		["n|gh"] = map_callback(function()
				helpers.picker("lsp_references")
			end)
			:with_buffer(buf)
			:with_noremap()
			:with_nowait()
			:with_silent()
			:with_desc("lsp: Show finder"),
		["n|gm"] = map_callback(function()
				helpers.picker("lsp_implementations")
			end)
			:with_buffer(buf)
			:with_noremap()
			:with_nowait()
			:with_silent()
			:with_desc("lsp: Show implementations"),
		["n|gci"] = map_cr("Lspsaga incoming_calls")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Show incoming calls"),
		["n|gco"] = map_cr("Lspsaga outgoing_calls")
			:with_silent()
			:with_buffer(buf)
			:with_desc("lsp: Show outgoing calls"),
		["n|<leader>lv"] = map_callback(function()
				helpers.toggle_virtuallines()
			end)
			:with_buffer(buf)
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Toggle virtual lines"),
		["n|<leader>lh"] = map_callback(function()
				helpers.toggle_inlayhint()
			end)
			:with_buffer(buf)
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Toggle inlay hints"),
	}
	bind.nvim_load_mapping(map)

	local ok, user_mappings = pcall(require, "user.keymap.completion")
	if ok and type(user_mappings.lsp) == "function" then
		require("modules.utils.keymap").replace(user_mappings.lsp(buf))
	end
end

return M
