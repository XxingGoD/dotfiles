--- @since 26.1.22

local const = require(".const")

local M = {}
local MAX_ITEMS_IN_CACHE = 10

function M.is_valid_utf8(str)
	return utf8.len(str) ~= nil
end

function M.utf8_sub(str, start_char, end_char)
	local start_byte = utf8.offset(str, start_char) -- Expects start_char to be a character index
	local end_byte = end_char and (utf8.offset(str, end_char + 1) or (#str + 1)) - 1 -- Expects end_char
	if not start_byte then
		return ""
	end
	return str:sub(start_byte, end_byte)
end
function M.is_literal_string(str)
	return str and str:gsub("([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1")
end
function M.path_quote(path)
	if not path or tostring(path) == "" then
		return path
	end
	local result = "'" .. string.gsub(tostring(path), "'", "'\\''") .. "'"
	return result
end

local function file_exists(path)
	local file = io.open(path, "rb")
	if file then
		file:close()
		return true
	end
	return false
end

function M.bin(cmd)
	if not cmd or tostring(cmd) == "" then
		return cmd
	end
	cmd = tostring(cmd)
	if cmd:find("/", 1, true) then
		return cmd
	end

	local seen = {}
	local path = (os.getenv("PATH") or "") .. ":/usr/local/bin:/usr/bin:/bin"
	for dir in path:gmatch("([^:]+)") do
		if dir ~= "" and not seen[dir] then
			seen[dir] = true
			local candidate = dir .. "/" .. cmd
			if file_exists(candidate) then
				return candidate
			end
		end
	end

	return cmd
end

function M.command_error(cmd, err)
	local detail = tostring(err or "unknown error"):gsub("%s+$", "")
	return string.format("Command `%s` failed: %s\n", cmd, detail)
end

M.force_render = ya.sync(function(_, _)
	(ui.render or ya.render)()
end)

M.set_state = ya.sync(function(state, key, value)
	state[key] = value
end)

M.get_state = ya.sync(function(state, key)
	return state[key]
end)

M.set_states = ya.sync(function(state, namespace, key, value, limit_cached_items)
	if not limit_cached_items then
		limit_cached_items = MAX_ITEMS_IN_CACHE
	end
	if not state[namespace] then
		state[namespace] = {}
	end
	local storage = state[namespace]
	if limit_cached_items and #storage > limit_cached_items then
		table.remove(storage, 1)
	end
	storage[key] = value
end)

M.get_states = ya.sync(function(state, namespace, key)
	local storage = state[namespace]
	if not storage then
		return nil
	end

	if storage then
		return storage[key]
	end
end)
function M.read_mediainfo_cached_file(file_path)
	local cached = M.get_states(const.STATE_KEY.cached_mediainfo, file_path)
	if cached then
		return cached
	end
	-- Open the file in read mode
	local file = io.open(file_path, "r")

	if file then
		-- Read the entire file content
		local content = file:read("*all")
		file:close()
		M.set_states(const.STATE_KEY.cached_mediainfo, file_path, content)
		return content
	end
end

M.current_file = ya.sync(function()
	local h = cx.active.current.hovered
	if not h then
		return
	end
	return tostring(h.url)
end)

function M.error(s, ...)
	ya.notify({ title = "mediainfo", content = string.format(s, ...), timeout = 3, level = "error" })
end

function M.info(s, ...)
	ya.notify({ title = "mediainfo", content = string.format(s, ...), timeout = 3, level = "info" })
end

return M
