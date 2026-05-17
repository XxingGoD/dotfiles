return function()
	require("modules.utils").load_plugin("codex", {
		terminal = {
			provider = "native",
			direction = "vertical",
			position = "right",
			size = 0.35,
			reuse = true,
			auto_insert_mode = true,
		},
		terminal_bridge = {
			path_format = "rel",
			path_prefix = "@",
			auto_attach = true,
			selection_mode = "content",
		},
	})
end
