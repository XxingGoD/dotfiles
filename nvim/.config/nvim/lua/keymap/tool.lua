local vim_path = require("core.global").vim_path
local bind = require("keymap.bind")
local map_cr = bind.map_cr
local map_cu = bind.map_cu
local map_cmd = bind.map_cmd
local map_callback = bind.map_callback
local helpers = require("keymap.helpers")

local function codex_terminal_exists()
	local ok, terminal = pcall(require, "codex.terminal")
	return ok and terminal.get_active_terminal_bufnr() ~= nil
end

local function codex_ensure_open()
	local codex = require("codex")
	if codex_terminal_exists() then
		return 0
	end
	codex.open()
	return 180
end

local function codex_send_current_path()
	local bufnr = vim.api.nvim_get_current_buf()
	local delay = codex_ensure_open()

	vim.defer_fn(function()
		if not vim.api.nvim_buf_is_valid(bufnr) then
			return
		end
		vim.api.nvim_buf_call(bufnr, function()
			vim.cmd("CodexSendPath")
		end)
	end, delay)
end

local function codex_send_range(command)
	local bufnr = vim.api.nvim_get_current_buf()
	local first = vim.fn.getpos("'<")[2]
	local last = vim.fn.getpos("'>")[2]
	if first == 0 or last == 0 then
		return
	end
	if first > last then
		first, last = last, first
	end

	local delay = codex_ensure_open()
	vim.defer_fn(function()
		if not vim.api.nvim_buf_is_valid(bufnr) then
			return
		end
		vim.api.nvim_buf_call(bufnr, function()
			vim.cmd(string.format("%d,%d%s", first, last, command))
		end)
	end, delay)
end

local mappings = {
	plugins = {
		-- Plugin: vim-fugitive
		["n|gps"] = map_cr("G push"):with_noremap():with_silent():with_desc("git: Push"),
		["n|gpl"] = map_cr("G pull"):with_noremap():with_silent():with_desc("git: Pull"),
		["n|<leader>gG"] = map_cu("Git"):with_noremap():with_silent():with_desc("git: Open git-fugitive"),

		-- Plugin: edgy
		["n|<C-n>"] = map_callback(function()
				require("edgy").toggle("left")
			end)
			:with_noremap()
			:with_silent()
			:with_desc("filetree: Toggle"),

		-- Plugin: nvim-tree
		["n|<F3>"] = map_cr("NvimTreeToggle"):with_noremap():with_silent():with_desc("filetree: Toggle"),
		["n|<leader>nt"] = map_cr("NvimTreeToggle"):with_noremap():with_silent():with_desc("filetree: Toggle"),
		["n|<leader>nf"] = map_cr("NvimTreeFindFile"):with_noremap():with_silent():with_desc("filetree: Find file"),
		["n|<leader>nr"] = map_cr("NvimTreeRefresh"):with_noremap():with_silent():with_desc("filetree: Refresh"),

		-- Plugin: sniprun
		["v|<leader>r"] = map_cr("SnipRun"):with_noremap():with_silent():with_desc("tool: Run code by range"),
		["n|<leader>r"] = map_cu([[%SnipRun]]):with_noremap():with_silent():with_desc("tool: Run code by file"),

		-- Plugin: toggleterm
		["t|<Esc><Esc>"] = map_cmd([[<C-\><C-n>]]):with_noremap():with_silent(), -- switch to normal mode in terminal.
		["n|<C-\\>"] = map_cr("ToggleTerm direction=horizontal")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle horizontal"),
		["i|<C-\\>"] = map_cmd("<Esc><Cmd>ToggleTerm direction=horizontal<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle horizontal"),
		["t|<C-\\>"] = map_cmd("<Cmd>ToggleTerm<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle horizontal"),
		["n|<A-\\>"] = map_cr("ToggleTerm direction=vertical")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle vertical"),
		["i|<A-\\>"] = map_cmd("<Esc><Cmd>ToggleTerm direction=vertical<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle vertical"),
		["t|<A-\\>"] = map_cmd("<Cmd>ToggleTerm<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle vertical"),
		["n|<F5>"] = map_cr("ToggleTerm direction=vertical")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle vertical"),
		["i|<F5>"] = map_cmd("<Esc><Cmd>ToggleTerm direction=vertical<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle vertical"),
		["t|<F5>"] = map_cmd("<Cmd>ToggleTerm<CR>"):with_noremap():with_silent():with_desc("terminal: Toggle vertical"),
		["n|<A-d>"] = map_cr("ToggleTerm direction=float")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle float"),
		["i|<A-d>"] = map_cmd("<Esc><Cmd>ToggleTerm direction=float<CR>")
			:with_noremap()
			:with_silent()
			:with_desc("terminal: Toggle float"),
		["t|<A-d>"] = map_cmd("<Cmd>ToggleTerm<CR>"):with_noremap():with_silent():with_desc("terminal: Toggle float"),
		["n|<leader>gg"] = map_callback(function()
				helpers.toggle_lazygit()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("git: Toggle lazygit"),

		-- Plugin: trouble
		["n|gt"] = map_cr("Trouble diagnostics toggle")
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Toggle trouble list"),
		["n|<leader>lw"] = map_cr("Trouble diagnostics toggle")
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Show workspace diagnostics"),
		["n|<leader>lp"] = map_cr("Trouble project_diagnostics toggle")
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Show project diagnostics"),
		["n|<leader>ld"] = map_cr("Trouble diagnostics toggle filter.buf=0")
			:with_noremap()
			:with_silent()
			:with_desc("lsp: Show document diagnostics"),

		-- Plugin: telescope
		["n|<C-p>"] = map_callback(function()
				helpers.picker("keymaps", {
					lhs_filter = function(lhs)
						return not string.find(lhs, "Þ")
					end,
				})
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Toggle command panel"),
		["n|<leader>fc"] = map_callback(function()
				helpers.telescope_collections(require("telescope.themes").get_dropdown())
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Open Telescope collections"),
		["n|<leader>ff"] = map_callback(function()
				require("search").open({ collection = "file" })
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Find files"),
		["n|<leader>fp"] = map_callback(function()
				require("search").open({ collection = "pattern" })
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Find patterns"),
		["v|<leader>fs"] = map_callback(function()
				local is_config = vim.uv.cwd() == vim_path
				if require("core.settings").search_backend == "fzf" then
					require("fzf-lua").grep_project({
						search = require("fzf-lua.utils").get_visual_selection(),
						rg_opts = "--column --line-number --no-heading --color=always --smart-case"
							.. (is_config and " --no-ignore --hidden --glob '!.git/*'" or ""),
					})
				else
					require("telescope-live-grep-args.shortcuts").grep_visual_selection(
						is_config and { additional_args = { "--no-ignore" } } or {}
					)
				end
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Find word under cursor"),
		["n|<leader>fg"] = map_callback(function()
				require("search").open({ collection = "git" })
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Locate Git objects"),
		["n|<leader>fd"] = map_callback(function()
				require("search").open({ collection = "dossier" })
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Retrieve dossiers"),
		["n|<leader>fm"] = map_callback(function()
				require("search").open({ collection = "misc" })
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Miscellaneous"),
		["n|<leader>fr"] = map_cr("Telescope resume")
			:with_noremap()
			:with_silent()
			:with_desc("tool: Resume last search"),
		["n|<leader>fR"] = map_callback(function()
				if require("core.settings").search_backend == "fzf" then
					require("fzf-lua").resume()
				end
			end)
			:with_noremap()
			:with_silent()
			:with_desc("tool: Resume last search"),

		-- Plugin: dap
		["n|<F6>"] = map_callback(function()
				require("dap").continue()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Run/Continue"),
		["n|<F7>"] = map_callback(function()
				require("dap").terminate()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Stop"),
		["n|<F8>"] = map_callback(function()
				require("dap").toggle_breakpoint()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Toggle breakpoint"),
		["n|<F9>"] = map_callback(function()
				require("dap").step_into()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Step into"),
		["n|<F10>"] = map_callback(function()
				require("dap").step_out()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Step out"),
		["n|<F11>"] = map_callback(function()
				require("dap").step_over()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Step over"),
		["n|<leader>db"] = map_callback(function()
				require("dap").set_breakpoint(vim.fn.input("Breakpoint condition: "))
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Set breakpoint with condition"),
		["n|<leader>dc"] = map_callback(function()
				require("dap").run_to_cursor()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Run to cursor"),
		["n|<leader>dl"] = map_callback(function()
				require("dap").run_last()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Run last"),
		["n|<leader>do"] = map_callback(function()
				require("dap").repl.open()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Open REPL"),
		["n|<leader>dC"] = map_callback(function()
				require("dapui").close()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("debug: Close debug UI"),

	-- Plugin: codex.nvim
	["n|<C-a>"] = map_callback(function()
				vim.ui.input({ prompt = "Codex> " }, function(input)
					if input == nil then
						return
					end
					if input == "" then
						require("codex").open()
						return
					end
					require("codex").open(input)
				end)
			end)
			:with_noremap()
			:with_silent()
			:with_desc("ai: Codex Ask"),
	["x|<C-a>"] = map_callback(function()
				codex_send_range("CodexSendSelection")
			end)
			:with_noremap()
			:with_silent()
			:with_desc("ai: Codex Send Selection"),
	["n|<C-x>"] = map_callback(function()
				codex_send_current_path()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("ai: Codex Send Path"),
	["x|<C-x>"] = map_callback(function()
				codex_send_range("CodexSendReference")
			end)
			:with_noremap()
			:with_silent()
			:with_desc("ai: Codex Send Reference"),
	["n|<C-.>"] = map_callback(function()
				require("codex").toggle()
			end)
			:with_noremap()
			:with_silent()
			:with_desc("ai: Codex Toggle"),
	},
}

bind.nvim_load_mapping(mappings.plugins)
