return function()
	require("modules.utils").load_plugin("paint", {
		highlights = {
			{
				filter = function(bufnr)
					return vim.bo[bufnr].filetype == "lua" and not require("core.bigfile").is_big(bufnr)
				end,
				pattern = "%s*%-%-%-%s*(@%w+)",
				hl = "Constant",
			},
			{
				filter = function(bufnr)
					return vim.bo[bufnr].filetype == "python" and not require("core.bigfile").is_big(bufnr)
				end,
				pattern = "%s*([_%w]+:)",
				hl = "Constant",
			},
		},
	})
end
