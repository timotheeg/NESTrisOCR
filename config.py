threads = 1
screenshot_per_field = True
stats_method = 'FIELD'
grid_nearest_neighbour_scaling = True
grid_check_5 = True

window_name = "OBS"

# Window coordinates in pixel from window's top-left corner as (X, Y, W, H)
window_coordinates = (, , , )

# All coordinates in tuples represent (X, Y, W, H) in ratio of window's capture area
# Types represent:
# * digits: Consecutive horizontal sequence of digits following supplied pattern
# * stats: Vertical list of consecutive digits following supplied pattern. The number of vertical items it the length of supplied labels
# * grid: represents a grid of blocks, grid size is given by pattern tuple (num_rows, num_columns)
# * next_piece: block recognition with next_piece specific alignment consideration
# * cur_piece: block recognition with cur_piece specific alignment consideration
# * controls: custom pattern recognition, looking for controller data (up, down, left, right, A, B)
fields = {
	"top_score": {
		"type":        "digits",
		"pattern":     "DDDDDD",
		"coordinates": (, , , )
	},
	"score": {
		"type":        "digits",
		"pattern":     "DDDDDD",
		"coordinates": (, , , )
	},
	"level": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (, , , )
	},
	"lines": {
		"type":        "digits",
		"pattern":     "DDD",
		"coordinates": (, , , )
	},
	"stats": {
		"type":        "stats",
		"labels":      ["T", "J", "Z", "O", "S", "L", "I"],
		"pattern":     "DDD",
		"coordinates": (, , , ),
		"wrap":        False
	},

	#das trainer
	"das": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (, , , )
	},
	#das trainer
	"cur_piece_das": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (, , , )
	},
	#das trainer
	"das_stats": {
		"type":        "stats",
		"labels":      ["great", "ok", "bad", "terrible"],
		"pattern":     "DDD",
		"coordinates": (, , , ),
		"wrap":        True
	},

	"board": {
		"type":        "grid",
		"pattern":     (20, 10),
		"coordinates": (, , , ),
		"binary":      True,
		"with_count":  True
	},

	"stats_board": {
		"type":        "grid",
		"pattern":     (2, 4),
		"coordinates": (, , , ),
		"binary":      True,
		"with_count":  False
	},

	"next_piece": {
		"type":        "next_piece"
		"coordinates": (, , , )
	},

	#das trainer
	"cur_piece": {
		"type":        "cur_piece",
		"coordinates": (, , , )
	}

	#das trainer
	"controls": {
		"type":        "controls",
		"coordinates": (, , , )
	}
}

