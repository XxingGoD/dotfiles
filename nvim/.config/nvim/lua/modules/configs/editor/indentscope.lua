return function()
	local utils = require("modules.utils")
	local mini_indentscope = require("mini.indentscope")

	local function set_hl()
		local colors = utils.get_palette()
		vim.api.nvim_set_hl(0, "MiniIndentscopeSymbol", {
			fg = colors.blue,
			nocombine = true,
		})
		vim.api.nvim_set_hl(0, "MiniIndentscopeSymbolOff", {
			fg = colors.surface2,
			nocombine = true,
		})
	end

	-- Fixed step timing feels smoother here than easing curves, which tend to
	-- visibly slow down at the scope edges.
	local function scope_animation()
		return 32
	end

	require("modules.utils").load_plugin("mini.indentscope", {
		symbol = "│",
		draw = {
			delay = 70,
			priority = 3,
			animation = scope_animation,
		},
		options = {
			border = "both",
			indent_at_cursor = true,
			try_as_border = true,
		},
		mappings = {
			object_scope = "",
			object_scope_with_border = "",
			goto_top = "",
			goto_bottom = "",
		},
	})

	set_hl()
	vim.api.nvim_create_autocmd("ColorScheme", {
		group = vim.api.nvim_create_augroup("MiniIndentscopeColors", { clear = true }),
		callback = set_hl,
	})
end
