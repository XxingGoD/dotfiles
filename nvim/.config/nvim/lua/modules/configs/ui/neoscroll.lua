return function()
	local neoscroll = require("neoscroll")

	require("modules.utils").load_plugin("neoscroll", {
		hide_cursor = true,
		stop_eof = true,
		use_local_scrolloff = false,
		respect_scrolloff = true,
		cursor_scrolls_alone = false,
		duration_multiplier = 1.25,
		easing = "circular",
		performance_mode = false,
		mappings = {},
	})

	local modes = { "n", "v", "x" }
	local keymaps = {
		["<C-u>"] = function()
			neoscroll.ctrl_u({ duration = 210, easing = "sine" })
		end,
		["<C-d>"] = function()
			neoscroll.ctrl_d({ duration = 210, easing = "sine" })
		end,
		["<C-b>"] = function()
			neoscroll.ctrl_b({ duration = 380, easing = "circular" })
		end,
		["<C-f>"] = function()
			neoscroll.ctrl_f({ duration = 380, easing = "circular" })
		end,
		["<C-y>"] = function()
			neoscroll.scroll(-0.1, { move_cursor = false, duration = 110, easing = "quadratic" })
		end,
		["<C-e>"] = function()
			neoscroll.scroll(0.1, { move_cursor = false, duration = 110, easing = "quadratic" })
		end,
		["zt"] = function()
			neoscroll.zt({ half_win_duration = 260, easing = "sine" })
		end,
		["zz"] = function()
			neoscroll.zz({ half_win_duration = 260, easing = "sine" })
		end,
		["zb"] = function()
			neoscroll.zb({ half_win_duration = 260, easing = "sine" })
		end,
	}

	for lhs, rhs in pairs(keymaps) do
		vim.keymap.set(modes, lhs, rhs, { silent = true })
	end
end
