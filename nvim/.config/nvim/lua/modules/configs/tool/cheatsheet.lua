return function()
	require("modules.utils").load_plugin("cheatsheet", {
		layout = {
			layout = {
				type = "flex",
				rows = { { { 0.4, "horizontal_grouped" } }, { { 0.6, "vertical_grouped" } } },
				horizontal_grouped = {
					{ " Telescope ", "Telescope" },
					{ " Git ", "Git" },
					{ " LSP ", "LSP" },
					{ " Terminal ", "Terminal" },
				},
				vertical_grouped = {
					{ " General ", "General" },
					{ " Buffer ", "Buffer" },
				},
			},
		},
		cheatsheet = {
			{
				icon = "⚡",
				heading = "General",
				key_value_pairs = {
					{ keys = "<C-s>", desc = "保存文件" },
					{ keys = "<C-z>", desc = "撤销" },
					{ keys = "<C-y>", desc = "重做" },
					{ keys = "<C-_>", desc = "注释切换" },
					{ keys = ":w", desc = "保存" },
					{ keys = ":q", desc = "退出" },
					{ keys = "jj", desc = "退出插入模式" },
					{ keys = "<F1>", desc = "快捷键手册" },
				},
			},
			{
				icon = "📦",
				heading = "Buffer",
				key_value_pairs = {
					{ keys = "<leader>bd", desc = "关闭当前 Buffer" },
					{ keys = "<leader>bn", desc = "新建 Buffer" },
					{ keys = "<A-i>", desc = "下一个 Buffer" },
					{ keys = "<A-o>", desc = "上一个 Buffer" },
				},
			},
			{
				icon = "🔍",
				heading = "Telescope",
				key_value_pairs = {
					{ keys = "<leader>ff", desc = "查找文件" },
					{ keys = "<leader>fg", desc = "Git 对象" },
					{ keys = "<leader>fs", desc = "搜索光标处" },
					{ keys = "<leader>fc", desc = "Collections" },
					{ keys = "<leader>fr", desc = "恢复搜索" },
					{ keys = "<C-p>", desc = "快捷键面板" },
				},
			},
			{
				icon = "📦",
				heading = "Git",
				key_value_pairs = {
					{ keys = "<leader>gg", desc = "打开 lazygit" },
					{ keys = "<leader>gp", desc = "Git push" },
					{ keys = "<leader>gl", desc = "Git pull" },
					{ keys = "<leader>gG", desc = "打开 git-fugitive" },
				},
			},
			{
				icon = "💻",
				heading = "Terminal",
				key_value_pairs = {
					{ keys = "<C-\\>", desc = "水平终端" },
					{ keys = "<A-\\>", desc = "垂直终端" },
					{ keys = "<A-d>", desc = "浮动终端" },
					{ keys = "<leader>h", desc = "水平终端" },
					{ keys = "<leader>i", desc = "浮动终端" },
				},
			},
			{
				icon = "⚙️",
				heading = "LSP",
				key_value_pairs = {
					{ keys = "gd", desc = "跳转定义" },
					{ keys = "gD", desc = "跳转声明" },
					{ keys = "gr", desc = "查找引用" },
					{ keys = "K", desc = "显示文档" },
					{ keys = "gh", desc = "LSP hover" },
					{ keys = "<leader>sp", desc = "预览定义" },
					{ keys = "<leader>so", desc = "切换符号大纲" },
					{ keys = "<leader>st", desc = "当前文件符号" },
					{ keys = "<leader>sw", desc = "工作区符号" },
					{ keys = "<F2>", desc = "重命名" },
					{ keys = "<leader>lw", desc = "工作区诊断" },
					{ keys = "<leader>ld", desc = "文档诊断" },
				},
			},
			{
				icon = "🐛",
				heading = "Debug",
				key_value_pairs = {
					{ keys = "<F6>", desc = "继续运行" },
					{ keys = "<F7>", desc = "停止" },
					{ keys = "<F8>", desc = "切换断点" },
					{ keys = "<F9>", desc = "步入" },
					{ keys = "<F10>", desc = "步出" },
					{ keys = "<F11>", desc = "步过" },
				},
			},
			{
				icon = "🔧",
				heading = "Which-Key 分组",
				key_value_pairs = {
					{ keys = "<leader>g", desc = "Git" },
					{ keys = "<leader>d", desc = "Debug" },
					{ keys = "<leader>s", desc = "Session / Symbols" },
					{ keys = "<leader>b", desc = "Buffer" },
					{ keys = "<leader>S", desc = "Search / Replace" },
					{ keys = "<leader>W", desc = "Window" },
					{ keys = "<leader>p", desc = "Package" },
					{ keys = "<leader>l", desc = "LSP" },
					{ keys = "<leader>f", desc = "Fuzzy Find" },
					{ keys = "<leader>n", desc = "Nvim Tree" },
					{ keys = "<leader>c", desc = "Chat" },
				},
			},
		},
	})
end
