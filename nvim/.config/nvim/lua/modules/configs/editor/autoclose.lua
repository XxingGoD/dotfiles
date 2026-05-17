return function()
	require("modules.utils").load_plugin("autoclose", {
		keys = {},
		options = {
			disable_when_touch = false,
			disabled_filetypes = {
				"alpha",
				"checkhealth",
				"dap-repl",
				"diff",
				"help",
				"log",
				"notify",
				"NvimTree",
				"Outline",
				"qf",
				"TelescopePrompt",
				"toggleterm",
				"undotree",
				"vimwiki",
			},
		},
	})
end
