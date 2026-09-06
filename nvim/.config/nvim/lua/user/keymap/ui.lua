local bind = require("keymap.bind")
local map_cr = bind.map_cr

return {
	["n|<leader>ad"] = map_cr("Alpha"):with_noremap():with_silent():with_desc("ui: Return to dashboard"),
	["n|<leader>bc"] = map_cr("bdelete"):with_noremap():with_silent():with_desc("buffer: Close"),
	["n|<leader>Wc"] = map_cr("close"):with_noremap():with_silent():with_desc("window: Close"),
	["n|<leader>bd"] = false,
	["n|bc"] = false,
}
