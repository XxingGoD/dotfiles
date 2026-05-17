return function()
	local transparent_background = require("core.settings").transparent_background

	require("modules.utils").load_plugin("tokyonight", {
		style = "night",
		transparent = transparent_background,
		terminal_colors = true,
		styles = {
			sidebars = transparent_background and "transparent" or "dark",
			floats = transparent_background and "transparent" or "dark",
		},
	})
end
