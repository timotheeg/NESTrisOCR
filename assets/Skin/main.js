
if (!CanvasRenderingContext2D.prototype.clear) {
	CanvasRenderingContext2D.prototype.clear = function (preserveTransform) {
		if (preserveTransform) {
			this.save();
			this.setTransform(1, 0, 0, 1, 0, 0);
		}

		this.clearRect(0, 0, this.canvas.width, this.canvas.height);

		if (preserveTransform) {
			this.restore();
		}
	};
}


/*
const socket = new WebSocket('ws://127.0.0.1:3338');
socket.addEventListener('message', (frame => {
	try{
		onFrame(JSON.parse(frame.data));
	}
	catch(e) {
		// socket.close();
		console.error(e);
	}
}));
/**/

let timeline_idx = 0;
// interval = setInterval(() => {onFrame(frames[timeline_idx++])}, 16);

function oneFrame(debug=false) {
	const
		frame1_copy = {...frames[timeline_idx]},
		stage1 = frame1_copy.stage,

		frame2_copy = {...frames[timeline_idx+1]},
		stage2 = frame2_copy.stage;

	delete frame1_copy.stage;
	delete frame2_copy.stage;

	frame1_txt = ''
		+ timeline_idx
		+ ' '
		+ stage1[0]
		+ '\n'
		+ JSON.stringify(frame1_copy)
		+ ' '
		+ stage1[1].join('\n');

	frame2_txt = ''
		+ (timeline_idx + 1)
		+ ' '
		+ stage2[0]
		+ '\n'
		+ JSON.stringify(frame2_copy)
		+ ' '
		+ stage2[1].join('\n');

	document.querySelector('#cur_frame').value = frame1_txt;
	document.querySelector('#next_frame').value = frame2_txt;

	onFrame(frames[timeline_idx++], debug);
}

document.querySelector('#goto_next_frame').addEventListener('click', () => {
	oneFrame();
});

document.querySelector('#goto_next_frame_debug').addEventListener('click', () => {
	oneFrame(true);
});

document.querySelector('#skip .btn').addEventListener('click', () => {
	const
		input = document.querySelector('#skip .to').value,
		to = parseInt(input, 10);

	if (isNaN(to)) {
		console.error('invalid input', input);
		return;
	}

	while (timeline_idx < to ) {
		oneFrame();
	}
});


const
	fields = ['score', 'level', 'lines', 'cur_piece_das', 'cur_piece', 'next_piece'],
	dom    = new DomRefs(document);

var
	game = null,
	last_valid_state = null, 
	pending_piece = false,
	pending_line = false;

function onFrame(event, debug) {
	// TODO: detect a reset to zero and setup a new Game

	// transformation
	const transformed = {
		diff: {
			cleared_lines: 0,
			score:         0,
			cur_piece_das: false,
			cur_piece:     false,
			next_piece:    false,
			stage_top_row: false,
			stage_blocks:  false
		},

		score:         parseInt(event.score, 10),
		lines:         parseInt(event.lines, 10),
		level:         parseInt(event.level, 10),
		cur_piece_das: parseInt(event.cur_piece_das, 10),
		cur_piece:     event.cur_piece,
		next_piece:    event.next_piece,
		stage: {
			num_blocks: event.stage[0],
			top_row:    event.stage[1][0].join('')
		}
	};

	if (debug) {
		debugger;
	}

	let
		piece_entry =   false,
		cleared_lines = 0;

	if (!last_valid_state) {
		// waiting for one good frame
		// not guarantee to work well, we may want to gather good data over multiple frames
		if (transformed.cur_piece
			&& transformed.next_piece
			&& !isNaN(transformed.cur_piece_das)
			&& !isNaN(transformed.score)
			&& !isNaN(transformed.lines)
			&& !isNaN(transformed.level)
		) {
			game = new Game(transformed)
			last_valid_state = transformed;
		}

		return;
	}

	// TODO: game end state, and reset last_valid_state

	// populate diff
	const diff = transformed.diff;

	let has_new_piece = false;

	diff.level         = transformed.level !== last_valid_state.level;
	diff.cleared_lines = transformed.lines - last_valid_state.lines;
	diff.score         = transformed.score - last_valid_state.score;
	diff.cur_piece_das = transformed.cur_piece_das !== last_valid_state.cur_piece_das;
	diff.cur_piece     = transformed.cur_piece !== last_valid_state.cur_piece;
	diff.next_piece    = transformed.next_piece !== last_valid_state.next_piece;
	diff.stage_top_row = transformed.stage.top_row !== last_valid_state.stage.top_row;
	diff.stage_blocks  = transformed.stage.num_blocks - last_valid_state.stage.num_blocks;

	// check if a change to cur_piece_stats
	if (pending_piece || diff.cur_piece_das || diff.cur_piece || diff.next_piece) {
		if (transformed.cur_piece && transformed.next_piece && transformed.cur_piece_das) {
			has_new_piece = true;
			game.onPiece(transformed);
			renderPiece();
			pending_piece = false;

			Object.assign(last_valid_state, {
				cur_piece: transformed.cur_piece,
				next_piece: transformed.next_piece,
				cur_piece_das: transformed.cur_piece_das
			});
		}
		else {
			pending_piece = true;
		}
	}

	// check for score change
	if (pending_line || diff.score) {
		if (transformed.score && !isNaN(transformed.lines) && transformed.lines < 29) {
			game.onLine(transformed);
			renderLine();
			pending_line = false;

			Object.assign(last_valid_state, {
				score: transformed.score,
				lines: transformed.lines,
				level: transformed.level
			});
		}
		else {
			pending_line = true;
		}
	}

	if (transformed.stage.num_blocks % 2 == 1) return;

	if (diff.stage_blocks === 4) {
		last_valid_state.stage = transformed.stage;
		if (!has_new_piece) {
			pending_piece = true;
		}
	}
	else if (diff.stage_blocks < 0) {
		if (diff.stage_blocks % 10 === 0) {
			last_valid_state.stage = transformed.stage;
		}
	}
}


const line_categories = [
	[1, 'singles'],
	[2, 'doubles'],
	[3, 'triples'],
	[4, 'tetris']
];

function renderLine() {
	// massive population of all data shown on screen

	// do the small boxes first
	dom.tetris_rate.value.textContent = Math.round(game.data.lines[4].percent * 100).toString().padStart(2, '0') + '%';
	dom.level.value.textContent = game.data.level.toString().padStart(2, '0');
	dom.burn.count.textContent = game.data.burn.toString().padStart(2, '0');
	dom.lines.count.textContent = game.data.lines.count.toString().padStart(3, '0');

	dom.score.current.textContent = game.data.score.current.toString().padStart(6, '0');

	if (game.data.score.transition) {
		dom.score.transition.textContent = game.data.score.transition.toString().padStart(6, '0');
	}
	else {
		dom.score.transition.textContent = '------';
	}

	// lines and points
	dom.lines_stats.count.textContent = dom.lines.count.textContent;
	dom.points.count.textContent = game.data.score.current.toString().padStart(6, '0');

	line_categories.forEach(tuple => {
		const [num_lines, name] = tuple;

		dom.lines_stats[name].count.textContent = game.data.lines[num_lines].count.toString().padStart(3, '0');
		dom.lines_stats[name].lines.textContent = game.data.lines[num_lines].lines.toString().padStart(3, '0');
		dom.lines_stats[name].percent.textContent = Math.round(game.data.lines[num_lines].percent * 100).toString().padStart(2, '0') + '%';

		dom.points[name].count.textContent = game.data.points[num_lines].count.toString().padStart(6, '0');
		dom.points[name].percent.textContent = Math.round(game.data.points[num_lines].percent * 100).toString().padStart(2, '0') + '%';
	});

	dom.points.drops.count.textContent = game.data.points.drops.count.toString().padStart(6, '0');
	dom.points.drops.percent.textContent = Math.round(game.data.points.drops.percent * 100).toString().padStart(2, '0') + '%';

	// graph tetris rate
	dom.lines_stats.trt_ctx.clear();

	const
		pixel_size = 3,
		max_pixels = Math.floor(dom.lines_stats.trt_ctx.canvas.width / pixel_size),
		y_scale = dom.lines_stats.trt_ctx.canvas.height / 100
		cur_x = 0,
		to_draw = game.tetris_rate.slice(-1 * max_pixels);

	for (let idx = to_draw.length; idx--;) {
		dom.das.ctx.fillStyle = 'white';
		dom.das.ctx.fillRect(
			idx * pixel_size,
			Math.floor((100 - to_draw[idx]) * y_scale * pixel_size),
			pixel_size,
			pixel_size
		);
	}
}

function renderPiece() {
	dom.pieces.count.textContent = game.data.pieces.count.toString().padStart(3, '0');

	PIECES.forEach(name => {
		dom.pieces[name].count.textContent = game.data.pieces[name].count.toString().padStart(3, '0');
		dom.pieces[name].drought.textContent = game.data.pieces[name].drought.toString().padStart(2, '0');
		dom.pieces[name].percent.textContent = Math.round(game.data.pieces[name].percent * 100).toString().padStart(2, '0') + '%';

		dom.pieces[name].ctx.clear();
	});

	let
		pixel_size = 4;
		max_pixels = Math.floor(dom.pieces.T.ctx.canvas.width / (pixel_size + 1));
		cur_x = 0;
		to_draw = game.pieces.slice(-1 * max_pixels);

	for (let idx = to_draw.length; idx--;) {
		const
			p =     to_draw[idx].cur_piece,
			das =   to_draw[idx].cur_piece_das,
			color = DAS_COLORS[ DAS_THRESHOLDS[das] ],
			ctx =   dom.pieces[p].ctx;

		ctx.fillStyle = color;
		ctx.fillRect(
			idx * (pixel_size + 1),
			0,
			pixel_size,
			pixel_size
		);
	}

	// droughts
	dom.droughts.count.textContent = game.data.i_droughts.count.toString().padStart(3, '0');
	dom.droughts.cur.value.textContent = game.data.i_droughts.cur.toString().padStart(2, '0');
	dom.droughts.cur.gauge.style.width = `${game.data.i_droughts.cur * 2}px`;

	if (game.data.i_droughts.cur >= DROUGHT_PANIC_THRESHOLD) {
		dom.droughts.cur.element.classList.add('panic');
	}
	else {
		dom.droughts.cur.element.classList.remove('panic');
	}

	dom.droughts.max.value.textContent = game.data.i_droughts.max.toString().padStart(2, '0');
	dom.droughts.max.gauge.style.width = `${game.data.i_droughts.max * 2}px`;

	if (game.data.i_droughts.max == game.data.i_droughts.cur && game.data.i_droughts.max >= DROUGHT_PANIC_THRESHOLD) {
		dom.droughts.max.element.classList.add('panic');
	}
	else {
		dom.droughts.max.element.classList.remove('panic');
	}

	// das
	dom.das.cur.textContent = game.data.das.cur.toString().padStart(2, '0');
	dom.das.avg.textContent = game.data.das.avg.toFixed(1).padStart(4, '0');
	dom.das.great.textContent = game.data.das.great.toString().padStart(3, '0');
	dom.das.ok.textContent = game.data.das.ok.toString().padStart(3, '0');
	dom.das.bad.textContent = game.data.das.bad.toString().padStart(3, '0');

	// clear
	dom.das.ctx.clear();

	pixel_size = 3;
	max_pixels = Math.floor(dom.das.ctx.canvas.width / pixel_size);
	cur_x = 0;
	to_draw = game.pieces.slice(-1 * max_pixels);

	for (let idx = to_draw.length; idx--;) {
		const
			das = to_draw[idx].cur_piece_das,
			color = DAS_COLORS[ DAS_THRESHOLDS[das] ];

		dom.das.ctx.fillStyle = color;
		dom.das.ctx.fillRect(
			idx * pixel_size,
			(16 - das) * pixel_size,
			pixel_size,
			pixel_size
		);
	}
}