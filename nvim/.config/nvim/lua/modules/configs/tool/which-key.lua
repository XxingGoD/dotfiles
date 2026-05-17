return function()
	local icons = {
		ui = require("modules.utils.icons").get("ui"),
		misc = require("modules.utils.icons").get("misc"),
		git = require("modules.utils.icons").get("git", true),
		cmp = require("modules.utils.icons").get("cmp", true),
	}
	local normalize_desc = function(desc)
		if type(desc) ~= "string" then
			return desc
		end

		desc = desc:gsub("^%s*[%w_]+:%s*", "")
		return desc:gsub("^%l", string.upper)
	end

	require("modules.utils").load_plugin("which-key", {
		preset = "classic",
		delay = vim.o.timeoutlen,
		triggers = {
			{ "<auto>", mode = "nixso" },
		},
		plugins = {
			marks = true,
			registers = true,
			spelling = {
				enabled = true,
				suggestions = 20,
			},
			presets = {
				motions = false,
				operators = false,
				text_objects = true,
				windows = true,
				nav = true,
				z = true,
				g = true,
			},
		},
		win = {
			border = "none",
			padding = { 1, 2 },
			wo = { winblend = 0 },
		},
		expand = 1,
		replace = {
			desc = {
				{ "<Plug>%(?(.*)%)?", "%1" },
				{ "^%+", "" },
				{ "<[cC]md>", "" },
				{ "<[cC][rR]>", "" },
				{ "<[sS]ilent>", "" },
				{ "^lua%s+", "" },
				{ "^call%s+", "" },
				{ "^:%s*", "" },
				normalize_desc,
			},
		},
		icons = {
			group = "",
			rules = false,
			colors = false,
			breadcrumb = icons.ui.Separator,
			separator = icons.misc.Vbar,
			keys = {
				C = "C-",
				M = "A-",
				S = "S-",
				BS = "<BS> ",
				CR = "<CR> ",
				NL = "<NL> ",
				Esc = "<Esc> ",
				Tab = "<Tab> ",
				Up = "<Up> ",
				Down = "<Down> ",
				Left = "<Left> ",
				Right = "<Right> ",
				Space = "<Space> ",
				ScrollWheelUp = "<ScrollWheelUp> ",
				ScrollWheelDown = "<ScrollWheelDown> ",
			},
		},
		spec = {
			{ "<leader>b", group = icons.ui.Buffer .. " Buffer" },
			{ "<leader>d", group = icons.ui.Bug .. " Debug" },
			{ "<leader>f", group = icons.ui.Telescope .. " Find" },
			{ "<leader>g", group = icons.git.Git .. " Git" },
			{ "<leader>l", group = icons.misc.LspAvailable .. " LSP" },
			{ "<leader>n", group = icons.ui.FolderOpen .. " File Tree" },
			{ "<leader>p", group = icons.ui.Package .. " Package" },
			{ "<leader>s", group = icons.cmp.tmux .. " Session / Symbols" },
			{ "<leader>S", group = icons.ui.Search .. " Search & Replace" },
			{ "<leader>W", group = icons.ui.Window .. " Window" },
			{ "<leader>z", group = "Fold" },
		},
	})
end
