-- Please check `lua/core/settings.lua` to view the full list of configurable settings
local settings = {}

-- Examples
settings["use_ssh"] = false

settings["colorscheme"] = "tokyonight"
settings["transparent_background"] = true
settings["server_formatting_block_list"] = {
	clice = true,
}
settings["neovide_config"] = {
	opacity = 0.88,
	normal_opacity = 0.88,
	fullscreen = true,
	cursor_vfx_mode = "railgun",
	cursor_trail_size = 0.22,
	cursor_animation_length = 0.05,
	cursor_animate_in_insert_mode = true,
	cursor_animate_command_line = true,
	cursor_smooth_blink = true,
	cursor_vfx_particle_density = 10.0,
	cursor_vfx_particle_lifetime = 1.1,
	cursor_vfx_particle_phase = 1.2,
	cursor_vfx_particle_curl = 1.0,
	cursor_vfx_particle_speed = 18.0,
	cursor_vfx_opacity = 220.0,
}

return settings
