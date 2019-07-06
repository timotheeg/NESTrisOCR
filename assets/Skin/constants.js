const

	PIECES = ['T', 'J', 'Z', 'O', 'S', 'L', 'I'],

	LINES = {
		1: 'singles',
		2: 'doubles',
		3: 'triples',
		4: 'tetris',
	},

	DAS_COLORS = {
		great: 'green',
		ok:    'orange',
		bad:   'red'
	},

	DAS_THRESHOLDS = {
		0:  'bad',
		1:  'bad',
		2:  'bad',
		3:  'bad',
		4:  'bad',
		5:  'bad',
		6:  'bad',
		7:  'bad',
		8:  'bad',
		9:  'bad',
		10: 'ok',
		11: 'ok',
		12: 'ok',
		13: 'ok',
		14: 'ok',
		15: 'great',
		16: 'great'
	}, 

	DROUGHT_PANIC_THRESHOLD = 13,

	SCORE_BASES = [0, 40, 100, 300, 1200]
	
;