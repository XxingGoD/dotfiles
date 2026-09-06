local M = {}

local settings = require("core.settings")
local config = vim.tbl_deep_extend("force", {
	enabled = true,
	size_bytes = 2 * 1024 * 1024,
	line_count = 20000,
	combined_size_bytes = 256 * 1024,
	combined_line_count = 5000,
	undo_levels = 100,
}, settings.bigfile or {})

local states = {}
local treesitter_start_guarded = false

local buffer_options = {
	autoindent = false,
	cindent = false,
	copyindent = false,
	indentexpr = "",
	modeline = false,
	preserveindent = false,
	smartindent = false,
	swapfile = false,
	syntax = "",
	undofile = false,
	undolevels = config.undo_levels,
	synmaxcol = 200,
}

local window_options = {
	breakindent = false,
	colorcolumn = "",
	cursorcolumn = false,
	cursorline = false,
	foldcolumn = "0",
	foldenable = false,
	foldexpr = "0",
	foldmethod = "manual",
	list = false,
	relativenumber = false,
	signcolumn = "no",
	smoothscroll = false,
	spell = false,
	winbar = "",
	wrap = false,
}

local function enabled()
	return settings.load_big_files_faster ~= false and config.enabled ~= false
end

local function valid_buffer(bufnr)
	return type(bufnr) == "number" and vim.api.nvim_buf_is_valid(bufnr)
end

local function resolve_buffer(bufnr)
	if bufnr == nil or bufnr == 0 then
		return vim.api.nvim_get_current_buf()
	end
	return bufnr
end

local function set_buffer_var(bufnr, name, value)
	pcall(vim.api.nvim_buf_set_var, bufnr, name, value)
end

local function del_buffer_var(bufnr, name)
	pcall(vim.api.nvim_buf_del_var, bufnr, name)
end

local function ensure_state(bufnr)
	if not states[bufnr] then
		states[bufnr] = { active = false, buffer = {}, variables = {}, windows = {} }
	end
	return states[bufnr]
end

local function save_and_set_buffer_var(bufnr, name, value)
	local state = states[bufnr]
	if state.variables[name] == nil then
		local ok, current = pcall(vim.api.nvim_buf_get_var, bufnr, name)
		state.variables[name] = { exists = ok, value = current }
	end
	set_buffer_var(bufnr, name, value)
end

local function save_and_set_buffer_options(bufnr)
	local state = states[bufnr]
	for name, value in pairs(buffer_options) do
		if state.buffer[name] == nil then
			state.buffer[name] = vim.bo[bufnr][name]
		end
		vim.bo[bufnr][name] = value
	end
end

local function save_and_set_window_options(bufnr)
	local state = states[bufnr]
	for _, winid in ipairs(vim.fn.win_findbuf(bufnr)) do
		if vim.api.nvim_win_is_valid(winid) then
			state.windows[winid] = state.windows[winid] or {}
			for name, value in pairs(window_options) do
				if state.windows[winid][name] == nil then
					state.windows[winid][name] = vim.wo[winid][0][name]
				end
				vim.wo[winid][0][name] = value
			end
		end
	end
end

local function set_window_options(winid, options)
	if not vim.api.nvim_win_is_valid(winid) then
		return
	end

	for name, value in pairs(options) do
		pcall(function()
			vim.wo[winid][0][name] = value
		end)
	end
end

local function restore_window_options(bufnr, winid)
	local state = states[bufnr]
	local options = state and state.windows[winid]
	if not options then
		return
	end

	if vim.api.nvim_win_is_valid(winid) and vim.api.nvim_win_get_buf(winid) == bufnr then
		set_window_options(winid, options)
		state.windows[winid] = nil
	end
end

local function buf_leave_window(bufnr)
	local current = vim.api.nvim_get_current_win()
	if vim.api.nvim_win_is_valid(current) and vim.api.nvim_win_get_buf(current) == bufnr then
		return current
	end

	local windows = vim.fn.win_findbuf(bufnr)
	return #windows == 1 and windows[1] or nil
end

local function disable_runtime_features(bufnr)
	local state = states[bufnr]
	if vim.treesitter.highlighter.active[bufnr] then
		state.treesitter_active = true
		pcall(vim.treesitter.stop, bufnr)
	end

	if not state.base_disabled then
		if state.diagnostics_enabled == nil and type(vim.diagnostic.is_enabled) == "function" then
			local ok, diagnostic_state = pcall(vim.diagnostic.is_enabled, { bufnr = bufnr })
			if ok then
				state.diagnostics_enabled = diagnostic_state
			end
		end

		pcall(vim.diagnostic.enable, false, { bufnr = bufnr })
		pcall(vim.diagnostic.reset, nil, bufnr)
		if type(vim.lsp.inlay_hint.is_enabled) == "function" then
			local ok, inlay_hint_state = pcall(vim.lsp.inlay_hint.is_enabled, { bufnr = bufnr })
			if ok then
				state.inlay_hints_enabled = inlay_hint_state
			end
		end
		pcall(vim.lsp.inlay_hint.enable, false, { bufnr = bufnr })
		state.base_disabled = true
	end

    for _, client in ipairs(vim.lsp.get_clients({ bufnr = bufnr })) do
        if vim.bo[bufnr].filetype ~= "python" then
            pcall(vim.lsp.buf_detach_client, bufnr, client.id)
        end
    end

	local rainbow = package.loaded["rainbow-delimiters.lib"]
	if rainbow and rainbow.buffers then
		local current = rainbow.buffers[bufnr]
		if not state.rainbow_state_saved then
			state.rainbow_should_attach = current ~= false
			state.rainbow_state_saved = true
		end
		if type(current) == "table" and type(rainbow.detach) == "function" then
			pcall(rainbow.detach, bufnr)
		end
	end

	local autotag = package.loaded["nvim-ts-autotag.internal"]
	if autotag and type(autotag.is_supported) == "function" then
		local ok, supported = pcall(autotag.is_supported, vim.bo[bufnr].filetype)
		if ok and supported then
			local attached = pcall(vim.api.nvim_get_autocmds, {
				group = "nvim-ts-autotag-" .. bufnr,
			})
			state.autotag_was_attached = state.autotag_was_attached or attached
			if state.autotag_was_attached and type(autotag.detach) == "function" then
				pcall(autotag.detach, bufnr)
			end
		end
	end

	local ibl = package.loaded.ibl
	local ibl_config = package.loaded["ibl.config"]
	if ibl and ibl_config and type(ibl.setup_buffer) == "function" then
		if not state.ibl_overridden then
			local current = ibl_config.buffer_config and ibl_config.buffer_config[bufnr]
			state.ibl_had_config = current ~= nil
			state.ibl_config = current and vim.deepcopy(current) or nil
			state.ibl_overridden = true
		end
		pcall(ibl.setup_buffer, bufnr, { enabled = false })
	end

	local gitsigns = package.loaded.gitsigns
	if gitsigns and type(gitsigns.detach) == "function" and type(gitsigns.get_hunks) == "function" then
		local ok, hunks = pcall(gitsigns.get_hunks, bufnr)
		if ok and hunks ~= nil then
			pcall(gitsigns.detach, bufnr)
		end
	end

	local colors = package.loaded["nvim-highlight-colors"]
	if colors and type(colors.clear_highlights) == "function" then
		if not state.colors_state_saved then
			state.colors_was_active = type(colors.is_active) ~= "function" or colors.is_active()
			state.colors_state_saved = true
		end
		pcall(colors.clear_highlights, bufnr)
		state.colors_disabled = true
	end

	local dropbar = package.loaded["dropbar.utils.bar"]
	if dropbar and type(dropbar.exec) == "function" then
		pcall(dropbar.exec, "del", { buf = bufnr })
	end

	local cmp = package.loaded.cmp
	local cmp_config = package.loaded["cmp.config"]
	if cmp and cmp_config and cmp.setup and type(cmp.setup.buffer) == "function" then
		if not state.cmp_overridden then
			local current = cmp_config.buffers and cmp_config.buffers[bufnr]
			state.cmp_had_config = current ~= nil
			state.cmp_config = current and vim.deepcopy(current) or nil
			state.cmp_overridden = true
		end
		pcall(vim.api.nvim_buf_call, bufnr, function()
			cmp.setup.buffer({ enabled = false })
		end)
	end
end

local function restore_buffer_vars(bufnr, state)
	for name, saved in pairs(state.variables) do
		if saved.exists then
			set_buffer_var(bufnr, name, saved.value)
		else
			del_buffer_var(bufnr, name)
		end
	end
end

local function restore_runtime_features(bufnr, state)
	if state.diagnostics_enabled ~= nil then
		pcall(vim.diagnostic.enable, state.diagnostics_enabled, { bufnr = bufnr })
	end
	if state.inlay_hints_enabled ~= nil then
		pcall(vim.lsp.inlay_hint.enable, state.inlay_hints_enabled, { bufnr = bufnr })
	end

	local ibl = package.loaded.ibl
	local ibl_config = package.loaded["ibl.config"]
	if state.ibl_overridden and ibl and ibl_config then
		if state.ibl_had_config and type(ibl.setup_buffer) == "function" then
			pcall(ibl.setup_buffer, bufnr, state.ibl_config)
		elseif type(ibl_config.clear_buffer_config) == "function" then
			pcall(ibl_config.clear_buffer_config, bufnr)
			if type(ibl.refresh) == "function" then
				pcall(ibl.refresh, bufnr)
			end
		end
	end

	local cmp = package.loaded.cmp
	local cmp_config = package.loaded["cmp.config"]
	if state.cmp_overridden and cmp and cmp.setup and type(cmp.setup.buffer) == "function" then
		if state.cmp_had_config then
			pcall(vim.api.nvim_buf_call, bufnr, function()
				cmp.setup.buffer(state.cmp_config)
			end)
		elseif cmp_config and cmp_config.buffers then
			cmp_config.buffers[bufnr] = nil
		end
	end

	vim.schedule(function()
		if not valid_buffer(bufnr) or M.is_big(bufnr) then
			return
		end

		vim.bo[bufnr].autoindent = false
		vim.bo[bufnr].cindent = false
		vim.bo[bufnr].copyindent = false
		vim.bo[bufnr].indentexpr = ""
		vim.bo[bufnr].preserveindent = false
		vim.bo[bufnr].smartindent = false
		pcall(vim.treesitter.start, bufnr)

		local rainbow = package.loaded["rainbow-delimiters.lib"]
		if
			state.rainbow_state_saved
			and state.rainbow_should_attach
			and rainbow
			and type(rainbow.attach) == "function"
		then
			pcall(rainbow.attach, bufnr)
		end

		local autotag = package.loaded["nvim-ts-autotag.internal"]
		if state.autotag_was_attached and autotag and type(autotag.attach) == "function" then
			pcall(vim.api.nvim_buf_call, bufnr, function()
				autotag.attach(bufnr)
			end)
		end

		local gitsigns = package.loaded.gitsigns
		if gitsigns and type(gitsigns.attach) == "function" then
			pcall(gitsigns.attach, { bufnr = bufnr, trigger = "bigfile_restore" })
		end

		local colors = package.loaded["nvim-highlight-colors"]
		if
			state.colors_disabled
			and state.colors_was_active
			and colors
			and type(colors.refresh_highlights) == "function"
		then
			pcall(colors.refresh_highlights, bufnr, true)
		end

		local dropbar = package.loaded["dropbar.utils.bar"]
		if dropbar and type(dropbar.attach) == "function" then
			for _, winid in ipairs(vim.fn.win_findbuf(bufnr)) do
				pcall(dropbar.attach, bufnr, winid)
			end
		end

		pcall(vim.api.nvim_exec_autocmds, "FileType", {
			buf = bufnr,
			group = "nvim.lsp.enable",
			modeline = false,
		})
	end)
end

local function emit_bigfile(bufnr)
	vim.api.nvim_exec_autocmds("User", {
		pattern = "BigFile",
		modeline = false,
		data = {
			buf = bufnr,
			reason = vim.b[bufnr].bigfile_reason,
			size = vim.b[bufnr].bigfile_size,
			lines = vim.b[bufnr].bigfile_lines,
		},
	})
end

function M.is_big(bufnr)
	bufnr = resolve_buffer(bufnr)
	return valid_buffer(bufnr) and states[bufnr] ~= nil and states[bufnr].active == true
end

function M.apply(bufnr)
	bufnr = resolve_buffer(bufnr)
	local state = states[bufnr]
	if not state or not state.active or not valid_buffer(bufnr) then
		return
	end

	save_and_set_buffer_var(bufnr, "large_file", true)
	save_and_set_buffer_var(bufnr, "minicursorword_disable", true)
	save_and_set_buffer_var(bufnr, "miniindentscope_disable", true)
	save_and_set_buffer_var(bufnr, "matchup_matchparen_enabled", 0)
	save_and_set_buffer_var(bufnr, "sleuth_automatic", false)

	save_and_set_buffer_options(bufnr)
	save_and_set_window_options(bufnr)
	disable_runtime_features(bufnr)
end

function M.restore(bufnr)
	bufnr = resolve_buffer(bufnr)
	local state = states[bufnr]
	if not state then
		return
	end

	if not valid_buffer(bufnr) then
		states[bufnr] = nil
		return
	end

	state.active = false
	for name, value in pairs(state.buffer) do
		pcall(function()
			vim.bo[bufnr][name] = value
		end)
	end
	for _, winid in ipairs(vim.tbl_keys(state.windows)) do
		restore_window_options(bufnr, winid)
	end

	restore_buffer_vars(bufnr, state)
	states[bufnr] = nil
	restore_runtime_features(bufnr, state)
end

local function mark(bufnr, reason, size, lines)
	local first_detection = not M.is_big(bufnr)
	local state = ensure_state(bufnr)
	state.active = true
	save_and_set_buffer_var(bufnr, "bigfile", true)
	save_and_set_buffer_var(bufnr, "large_file", true)
	save_and_set_buffer_var(bufnr, "bigfile_reason", reason)
	save_and_set_buffer_var(bufnr, "bigfile_size", size or 0)
	save_and_set_buffer_var(bufnr, "bigfile_lines", lines or 0)
	M.apply(bufnr)

	if first_detection then
		emit_bigfile(bufnr)
	end
end

local function file_stat(bufnr)
	local name = vim.api.nvim_buf_get_name(bufnr)
	if name == "" then
		return nil, nil
	end

	local stat = vim.uv.fs_stat(name)
	if not stat or stat.type ~= "file" then
		return nil, nil
	end
	return stat, name
end

local function count_file_lines(path, stop_at)
	local fd = vim.uv.fs_open(path, "r", 438)
	if not fd then
		return nil
	end

	local offset = 0
	local lines = 0
	local last_byte
	while true do
		local chunk = vim.uv.fs_read(fd, 64 * 1024, offset)
		if not chunk or chunk == "" then
			break
		end
		offset = offset + #chunk
		last_byte = chunk:sub(-1)
		local from = 1
		while true do
			local newline = chunk:find("\n", from, true)
			if not newline then
				break
			end
			lines = lines + 1
			if lines >= stop_at then
				vim.uv.fs_close(fd)
				return lines
			end
			from = newline + 1
		end
	end
	vim.uv.fs_close(fd)

	if offset == 0 then
		return 1
	end
	return lines + (last_byte == "\n" and 0 or 1)
end

local function threshold_reason(size, lines)
	if size and config.size_bytes > 0 and size >= config.size_bytes then
		return "size"
	end
	if lines and config.line_count > 0 and lines >= config.line_count then
		return "lines"
	end
	if
		size
		and lines
		and config.combined_size_bytes > 0
		and config.combined_line_count > 0
		and size >= config.combined_size_bytes
		and lines >= config.combined_line_count
	then
		return "size+lines"
	end
end

local function line_probe_limit(size)
	local limit = config.line_count > 0 and config.line_count or nil
	if
		size
		and config.combined_size_bytes > 0
		and config.combined_line_count > 0
		and size >= config.combined_size_bytes
	then
		limit = limit and math.min(limit, config.combined_line_count) or config.combined_line_count
	end
	return limit
end

local function detect_pre(bufnr)
	if not valid_buffer(bufnr) then
		return
	end
	if not enabled() or vim.bo[bufnr].buftype ~= "" then
		M.restore(bufnr)
		return
	end

	local stat, name = file_stat(bufnr)
	local size = stat and stat.size or nil
	local reason = threshold_reason(size, nil)
	if reason then
		mark(bufnr, reason, size, 0)
	elseif name then
		local probe_limit = line_probe_limit(size)
		local lines = probe_limit and count_file_lines(name, probe_limit) or nil
		reason = threshold_reason(size, lines)
		if reason then
			mark(bufnr, reason, size, lines)
		else
			M.restore(bufnr)
		end
	else
		M.restore(bufnr)
	end
end

local function detect_lines(bufnr)
	if not valid_buffer(bufnr) then
		states[bufnr] = nil
		return
	end
	if not enabled() or vim.bo[bufnr].buftype ~= "" then
		M.restore(bufnr)
		return
	end

	local stat = file_stat(bufnr)
	local size = stat and stat.size or 0
	local lines = vim.api.nvim_buf_line_count(bufnr)
	local reason = threshold_reason(size, lines)
	if M.is_big(bufnr) then
		save_and_set_buffer_var(bufnr, "bigfile_size", size)
		save_and_set_buffer_var(bufnr, "bigfile_lines", lines)
		M.apply(bufnr)
	elseif reason then
		mark(bufnr, reason, size, lines)
	else
		M.restore(bufnr)
	end
end

local function reapply_all()
	for _, bufnr in ipairs(vim.api.nvim_list_bufs()) do
		if M.is_big(bufnr) then
			M.apply(bufnr)
		end
	end
end

function M.setup()
	if not enabled() then
		return
	end

	if not treesitter_start_guarded then
		local treesitter_start = vim.treesitter.start
		vim.treesitter.start = function(bufnr, lang)
			local target = bufnr == nil and vim.api.nvim_get_current_buf() or bufnr
			if M.is_big(target) then
				return
			end
			return treesitter_start(bufnr, lang)
		end
		treesitter_start_guarded = true
	end

	local group = vim.api.nvim_create_augroup("nvimdots_bigfile", { clear = true })
	local pending_split
	local last_entered_winid = vim.api.nvim_get_current_win()
	vim.api.nvim_create_autocmd("BufReadPre", {
		group = group,
		callback = function(event)
			detect_pre(event.buf)
		end,
		desc = "Mark large files before plugin BufReadPre handlers",
	})
	vim.api.nvim_create_autocmd("BufReadPost", {
		group = group,
		callback = function(event)
			detect_lines(event.buf)
		end,
		desc = "Apply large-file mode using the final line count",
	})
	vim.api.nvim_create_autocmd("WinNewPre", {
		group = group,
		callback = function()
			local bufnr = vim.api.nvim_get_current_buf()
			pending_split = nil
			if M.is_big(bufnr) then
				local windows = {}
				for _, winid in ipairs(vim.api.nvim_list_wins()) do
					windows[winid] = true
				end
				pending_split = {
					bufnr = bufnr,
					source_winid = vim.api.nvim_get_current_win(),
					windows = windows,
				}
			end
		end,
		desc = "Remember the source window before splitting a large file",
	})
	vim.api.nvim_create_autocmd("WinNew", {
		group = group,
		callback = function()
			local split = pending_split
			pending_split = nil
			local source_winid = split and split.source_winid or last_entered_winid
			if not vim.api.nvim_win_is_valid(source_winid) then
				return
			end

			local bufnr = split and split.bufnr or vim.api.nvim_win_get_buf(source_winid)
			if not M.is_big(bufnr) then
				return
			end

			local new_winid
			if split then
				for _, winid in ipairs(vim.api.nvim_list_wins()) do
					if not split.windows[winid] then
						new_winid = winid
						break
					end
				end
			else
				local current = vim.api.nvim_get_current_win()
				if current ~= source_winid then
					new_winid = current
				end
			end

			local state = states[bufnr]
			local source = state and state.windows[source_winid]
			if not new_winid or not vim.api.nvim_win_is_valid(new_winid) or not source then
				return
			end

			local win_config = vim.api.nvim_win_get_config(new_winid)
			local special_window = win_config.relative ~= "" or win_config.external == true
			if vim.api.nvim_win_get_buf(new_winid) == bufnr then
				if not special_window then
					state.windows[new_winid] = vim.deepcopy(source)
				end
				M.apply(bufnr)
			elseif not special_window then
				set_window_options(new_winid, source)
			end
		end,
		desc = "Preserve source options in windows created from a large file",
	})
	vim.api.nvim_create_autocmd({ "FileType", "BufWinEnter", "WinEnter", "InsertEnter" }, {
		group = group,
		callback = function(event)
			if M.is_big(event.buf) then
				M.apply(event.buf)
				vim.schedule(function()
					if M.is_big(event.buf) then
						M.apply(event.buf)
					end
				end)
			end
			if event.event == "WinEnter" then
				last_entered_winid = vim.api.nvim_get_current_win()
			end
		end,
		desc = "Keep local options degraded after ftplugins and window changes",
	})
	vim.api.nvim_create_autocmd("BufLeave", {
		group = group,
		callback = function(event)
			if M.is_big(event.buf) then
				local bufnr = event.buf
				local winid = buf_leave_window(bufnr)
				if not winid then
					return
				end
				restore_window_options(bufnr, winid)

				vim.schedule(function()
					if not vim.api.nvim_win_is_valid(winid) then
						return
					end

					local current_buf = vim.api.nvim_win_get_buf(winid)
					if current_buf == bufnr and M.is_big(bufnr) then
						M.apply(bufnr)
					end
				end)
			end
		end,
		desc = "Restore window-local options when leaving a large-file buffer",
	})
	vim.api.nvim_create_autocmd("LspAttach", {
		group = group,
		callback = function(event)
			if M.is_big(event.buf) then
				M.apply(event.buf)
			end
		end,
		desc = "Detach LSP clients from large files",
	})
	vim.api.nvim_create_autocmd("User", {
		group = group,
		pattern = "LazyLoad",
		callback = function()
			vim.schedule(reapply_all)
		end,
		desc = "Disable newly loaded plugins in existing large buffers",
	})
	vim.api.nvim_create_autocmd("BufWipeout", {
		group = group,
		callback = function(event)
			local bufnr = event.buf
			vim.schedule(function()
				if not valid_buffer(bufnr) then
					states[bufnr] = nil
				end
			end)
		end,
	})

	vim.api.nvim_create_user_command("BigFileInfo", function()
		local bufnr = vim.api.nvim_get_current_buf()
		if not M.is_big(bufnr) then
			vim.notify("Large-file mode is not active for this buffer")
			return
		end
		vim.notify(
			string.format(
				"Large-file mode: %s (%d bytes, %d lines)",
				vim.b[bufnr].bigfile_reason,
				vim.b[bufnr].bigfile_size,
				vim.b[bufnr].bigfile_lines
			)
		)
	end, { desc = "Show large-file mode status" })
end

M.config = config

return M
