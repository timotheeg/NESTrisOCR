calibrate = False
profile = 'original'
threads = 1
screenshot_per_field = True

window_name = "OBS"

# Window coordinates in pixel from window's top-left corner as (X, Y, W, H)
window_coordinates = (, , , )

# All coordinates in tuples represent (X, Y, W, H) in ratio of window's capture area
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
		"binary":      True
	},

	"stats_board": {
		"type":        "grid",
		"pattern":     (2, 4),
		"coordinates": (, , , ),
		"binary":      True
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

