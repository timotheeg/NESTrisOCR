class Game {
	constructor(start_level) {

		// will store all pieces that have been played in the game
		this.pieces = [];

		this.data = {
			start_level,

			level: start_level,
			burn:  0,

			score: {
				running:    0,
				transition: null
			},

			i_droughts: {
				cur: 0,
				max: 0
			},

			das: {
				cur:   0,
				total: 0, // running total, used for average computation
				avg:   0,
				great: 0,
				ok:    0,
				bad:   0
			},

			pieces: {
				count: 0
			},

			lines: {
				count: 0,
			},

			points: {
				count: 0,
				down: {
					count:   0,
					percent: 0
				}
			}
		}

		PIECES.forEach(name => {
			this.data.pieces[name] = {
				count:   0,
				percent: 0,
				drought: 0
			}
		});

		[1, 2, 3, 4].forEach(name => {
			this.data.lines[name] = {
				count:   0,
				lines:   0,
				percent: 0
			};

			this.data.points[name] = {
				count:   0,
				percent: 0
			};
		});
	}

	// event: {score, level, lines, das, cur_piece, next_piece, }
	onPiece(event) {
		const p = event.cur_piece;

		this.data.pieces.count++;
		this.data.pieces[p].num++;

		PIECES.forEach(name => {
			const stats = this.data.pieces[name];

			stats.percent = stats.count / this.data.pieces.count;
			stats.drought++;
		});

		this.data.pieces[p].drought = 0;

		if (p != 'I') {
			this.i_droughts.cur++;

			if (this.i_droughts.cur > this.i_droughts.max) {
				this.i_droughts.max = this.i_droughts.cur;
			}
		}
		else {
			this.i_droughts.cur = 0;
		}

		this.data.pieces[p].drought = 0;

		// update das
		const das_stats = this.data.das;
		das_stats.cur   =  event.cur_piece_das;
		das_stats.total += event.cur_piece_das;
		das_stats.avg   =  das_stats.total / (this.pieces.length + 1);
		das_stats[DAS_THRESHOLDS[das_stats.cur]]++; // great, ok, bad

		this.pieces.push(event);
	}

	onLine(event) {
		const
			num_lines =    event.lines - this.data.lines.count,
			lines_score =  this.getScore(this.data.level, num_lines),
			actual_score = event.score - this.data.score.running;

		if (lines_score < actual_score) {
			const down_score = actual_score - expected_min_score;

			this.data.points.down += down_score;
		}

		// update total lines
		this.data.lines.count = event.lines;

		// update lines stats for clearing type (single, double, etc...)
		this.data.lines[num_lines].count += 1;
		this.data.lines[num_lines].lines += num_lines;

		// update points stats for clearing type (single, double, etc...)
		this.data.points.count = event.score;
		this.data.points[num_lines].count += lines_score;

		// update percentages for everyone
		for (const clear_type=4; clear_type--;) {
			const line_stats = this.data.lines[clear_type];
			line_stats.percent = line_stats.lines / this.data.lines.count;

			const point_stats = this.data.points[clear_type];
			point_stats.percent = point_stats.count / event.score;
		}

		// update stat for down
		this.data.points.down.percent = this.data.points.down.count / event.score;

		// check transition score
		if (event.level > this.data.level) {
			if (event.level > this.data.start_level) {
				this.data.score.transition = event.score;
			}
		}

		// update level
		this.data.level = event.level;

		// update burn if needed
		if (num_lines < 4) {
			this.data.burn += num_lines;
		}

		// should this be called here or somewhere else?
		this.onPiece(event);
	}

	getScore(level, num_lines) {
		return SCORE_BASES[num_lines] * (level + 1)
	}

	toString(encoding='json') {
		return JSON.stringify(this.data);
	}
}