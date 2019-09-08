threads = 1
screenshot_per_field = True
stats_method = 'field' # 'field' or 'text'
grid_method = 'scale' # 'scale', 'pixel'
block_method = '5px' # 1px , 5px

window_name = "OBS"

# Window coordinates in pixel from window's top-left corner as (X, Y, W, H)
window_coordinates = (0, 0, 0, 0)

# All coordinates in tuples represent (X, Y, W, H) in ratio of window's capture area
# Types represent:
# * digits: Consecutive horizontal sequence of digits following supplied pattern
# ** patterns for digits.
# *** A = 0->9 + A->F,
# *** D = 0->9
# * stats: Vertical list of consecutive digits following supplied pattern. The number of vertical items it the length of supplied labels
# * grid: represents a grid of blocks, grid size is given by pattern tuple (num_rows, num_columns)
# * next_piece: block recognition with next_piece specific alignment consideration
# * cur_piece: block recognition with cur_piece specific alignment consideration
# * controls: custom pattern recognition, looking for controller data (up, down, left, right, A, B)
fields = {
	"top_score": {
		"type":        "digits",
		"pattern":     "ADDDDD",
		"coordinates": (0, 0, 0, 0)
	},
	"score": {
		"type":        "digits",
		"pattern":     "ADDDDD",
		"coordinates": (0, 0, 0, 0)
	},
	"level": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (0, 0, 0, 0)
	},
	"lines": {
		"type":        "digits",
		"pattern":     "DDD",
		"coordinates": (0, 0, 0, 0)
	},
	"stats": {
		"type":        "stats",
		"labels":      ["T", "J", "Z", "O", "S", "L", "I"],
		"pattern":     "DDD",
		"coordinates": (0, 0, 0, 0),
		"wrap":        False
	},
	#das trainer
	"das": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (0, 0, 0, 0)
	},
	#das trainer
	"cur_piece_das": {
		"type":        "digits",
		"pattern":     "DD",
		"coordinates": (0, 0, 0, 0)
	},
	#das trainer
	"das_stats": {
		"type":        "stats",
		"labels":      ["great", "ok", "bad", "terrible"],
		"pattern":     "DDD",
		"coordinates": (0, 0, 0, 0),
		"wrap":        True
	},
	"board": {
		"type":        "grid",
		"pattern":     (20, 10),
		"coordinates": (0, 0, 0, 0),
		"binary":      True,
		"with_count":  True
	},
	"stats_board": {
		"type":        "grid",
		"pattern":     (2, 4),
		"coordinates": (0, 0, 0, 0),
		"binary":      True,
		"with_count":  False
	},
	"next_piece": {
		"type":        "next_piece",
		"coordinates": (0, 0, 0, 0)
	},
	#das trainer
	"cur_piece": {
		"type":        "cur_piece",
		"coordinates": (0, 0, 0, 0)
	},
	#das trainer
	"controls": {
		"type":        "controls",
		"coordinates": (0, 0, 0, 0),
		"wrap":        True
	}
}

