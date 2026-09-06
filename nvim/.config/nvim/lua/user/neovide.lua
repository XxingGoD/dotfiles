local M = {}

function M.apply()
	if not vim.g.neovide then
		return
	end

	vim.api.nvim_set_hl(0, "CursorNeon", { fg = "#081018", bg = "#00F5D4" })
	vim.api.nvim_set_hl(0, "CursorInsertNeon", { fg = "#0E0B16", bg = "#FF4FD8" })
	vim.api.nvim_set_hl(0, "CursorReplaceNeon", { fg = "#111111", bg = "#F9F871" })
	vim.api.nvim_set_hl(0, "TermCursorNeon", { fg = "#081018", bg = "#7DF9FF" })
end

return M
