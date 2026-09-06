local tools = {}

tools["kawre/leetcode.nvim"] = {
	lazy = false,
	build = ":TSUpdate html",
	dependencies = {
		"MunifTanjim/nui.nvim",
		"nvim-telescope/telescope.nvim",
		"nvim-lua/plenary.nvim",
	},
	config = function()
		require("leetcode").setup({
			---@type string
			cookie = vim.env.LEETCODE_COOKIE or "", -- LeetCode session cookie (get it from browser)
			---@type string
			session = vim.env.LEETCODE_SESSION or "", -- LeetCode CSRF token (get it from browser)
			---@type string
			url = "https://leetcode.com",
			---@type string
			graphql_endpoint = "https://leetcode.com/graphql",
			cache = {
				enable = true,
				path = vim.fn.stdpath("cache") .. "/leetcode",
			},
			console = {
				close_on_exit = true,
			},
			statusline = {
				enabled = true,
			},
			hooks = {},
			cn = {
				enabled = true,
				translator = true,
				translate_problems = true,
			},
			---@type table<string, string>
			languages = {}, -- Language extension mapping
		})
	end,
}

return tools
