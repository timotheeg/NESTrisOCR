
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


/**/
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
	dom = new DomRefs(document),

	PIECE_COOLDOWN_FRAMES  = 10;



var
	game = null,
	last_valid_state = null,
	pending_game = false,
	pending_piece = false,
	pending_line = false,
	new_piece_cooldown_frames = 0;

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
			game = new Game(transformed);
			clearStage();
			renderPiece(transformed);
			renderLine(transformed);
			last_valid_state = { ...transformed };
			pending_piece = pending_line = true;
		}
		else {
			return;
		}
	}

	// TODO: game end state, and reset last_valid_state

	new_piece_cooldown_frames--;

	// populate diff
	const diff = transformed.diff;

	diff.level         = transformed.level !== last_valid_state.level;
	diff.cleared_lines = transformed.lines - last_valid_state.lines;
	diff.score         = transformed.score - last_valid_state.score;
	diff.cur_piece_das = transformed.cur_piece_das !== last_valid_state.cur_piece_das;
	diff.cur_piece     = transformed.cur_piece !== last_valid_state.cur_piece;
	diff.next_piece    = transformed.next_piece !== last_valid_state.next_piece;
	diff.stage_top_row = transformed.stage.top_row !== last_valid_state.stage.top_row;
	diff.stage_blocks  = transformed.stage.num_blocks - last_valid_state.stage.num_blocks;

	if (diff.score && transformed.score === 0) {
		// new game started
		if (isNaN(transformed.lines) || isNaN(transformed.level) || transformed.level > 29 ) {
			return; // but not fully formed valid state
		}

		game = new Game(transformed);
		clearStage();
		renderLine(transformed);
		last_valid_state = { ...transformed };
		pending_piece = true;
	}

	// check if a change to cur_piece_stats
	if (pending_piece || diff.cur_piece_das || diff.cur_piece || diff.next_piece) {
		if (transformed.cur_piece && transformed.next_piece && transformed.cur_piece_das) {
			new_piece_cooldown_frames = PIECE_COOLDOWN_FRAMES;
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
		if (
			transformed.score
			&& !isNaN(transformed.lines)
			&& !isNaN(transformed.level)
			&& transformed.level < 30
			&& diff.cleared_lines >= 0
			&& diff.cleared_lines <= 4
		) {
			if (diff.score > 20 && diff.cleared_lines <= 0) {
				pending_line = true;
			}
			else {
				game.onLine(transformed);
				renderLine();
				pending_line = false;

				Object.assign(last_valid_state, {
					score: transformed.score,
					lines: transformed.lines,
					level: transformed.level
				});
			}
		}
		else {
			pending_line = true;
		}
	}

	if (transformed.stage.num_blocks % 2 == 1) return;

	if (diff.stage_blocks === 4) {
		last_valid_state.stage = transformed.stage;

		if (new_piece_cooldown_frames <= 0) {
			pending_piece = true;
		}
	}
	else if (diff.stage_blocks < 0) {
		if (diff.stage_blocks % 10 === 0) { // works no matter how many lines are cleared!
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

function clearStage() {
	dom.droughts.cur.ctx.clear();
	dom.droughts.last.ctx.clear();
	dom.droughts.max.ctx.clear();
}

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
		dom.lines_stats[name].percent.textContent = Math.round(game.data.lines[num_lines].percent * 100).toString().padStart(2, '0').padStart(3, ' ') + '%';

		dom.points[name].count.textContent = game.data.points[num_lines].count.toString().padStart(6, '0');
		dom.points[name].percent.textContent = Math.round(game.data.points[num_lines].percent * 100).toString().padStart(2, '0').padStart(3, ' ') + '%';
	});

	dom.points.drops.count.textContent = game.data.points.drops.count.toString().padStart(6, '0');
	dom.points.drops.percent.textContent = Math.round(game.data.points.drops.percent * 100).toString().padStart(2, '0').padStart(3, ' ') + '%';

	// graph tetris rate
	dom.lines_stats.trt_ctx.clear();

	const
		ctx = dom.lines_stats.trt_ctx,
		pixel_size = 4,
		max_pixels = Math.floor(ctx.canvas.width / (pixel_size + 1)),
		y_scale = (ctx.canvas.height - pixel_size) / pixel_size,
		cur_x = 0,
		to_draw = game.tetris_rate.slice(-1 * max_pixels);

	for (let idx = to_draw.length; idx--;) {
		ctx.fillStyle = 'white';
		ctx.fillRect(
			idx * (pixel_size + 1),
			Math.round((1 - to_draw[idx]) * y_scale * pixel_size),
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
		idx,
		pixel_size = 4;
		max_pixels = Math.floor(dom.pieces.T.ctx.canvas.width / (pixel_size + 1));
		cur_x = 0;
		to_draw = game.pieces.slice(-1 * max_pixels);

	for (idx = to_draw.length; idx--;) {
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
	// TODO: Counter can go to 99 but bar should stop at max width
	// TODO: Use Canvas rather than span
	dom.droughts.count.textContent = game.data.i_droughts.count.toString().padStart(3, '0');
	dom.droughts.cur.value.textContent = game.data.i_droughts.cur.toString().padStart(2, '0');
	dom.droughts.last.value.textContent = game.data.i_droughts.last.toString().padStart(2, '0');
	dom.droughts.max.value.textContent = game.data.i_droughts.max.toString().padStart(2, '0');

	pixel_size = 4;
	max_pixels = Math.floor(dom.droughts.cur.ctx.canvas.width / (pixel_size + 1));
	color = 'orange';

	const
		cur_drought  = game.data.i_droughts.cur,
		cur_ctx      = dom.droughts.cur.ctx,

		last_drought = game.data.i_droughts.last,
		last_ctx     = dom.droughts.last.ctx,

		max_drought  = game.data.i_droughts.max,
		max_ctx      = dom.droughts.max.ctx;

	if (cur_drought > 0) {
		if (cur_drought <= max_pixels) {
			cur_ctx.fillStyle = color;
			cur_ctx.fillRect(
				(cur_drought - 1) * (pixel_size + 1),
				0,
				pixel_size,
				cur_ctx.canvas.height
			);
		}

		if (max_drought === cur_drought) {
			// draw the same block current has
			max_ctx.fillStyle = color;
			max_ctx.fillRect(
				(max_drought - 1) * (pixel_size + 1),
				0,
				pixel_size,
				max_ctx.canvas.height
			);
		}
	}
	else {
		// clear current but not max (only a new game would clear max)
		cur_ctx.clear();
	}

	// we clear and redraw the last gauge,
	// could be optimize by storing previous value and redraw on change,
	// but this will do for now
	last_ctx.clear();
	last_ctx.fillStyle = color;
	for (idx = Math.min(last_drought, max_pixels); idx-- > 0; ) {
		last_ctx.fillRect(
			idx * (pixel_size + 1),
			0,
			pixel_size,
			last_ctx.canvas.height
		);
	}

	if (game.data.i_droughts.cur >= DROUGHT_PANIC_THRESHOLD) {
		if (game.data.i_droughts.max == game.data.i_droughts.cur) {
			dom.droughts.element.classList.remove('panic');
			dom.droughts.element.classList.add('max_panic'); // doing this to synchronize animation
		}
		else {
			dom.droughts.element.classList.remove('max_panic');
			dom.droughts.element.classList.add('panic');
		}
	}
	else {
		dom.droughts.element.classList.remove('max_panic');
		dom.droughts.element.classList.remove('panic');
	}

	// das
	dom.das.cur.textContent = game.data.das.cur.toString().padStart(2, '0');
	dom.das.avg.textContent = game.data.das.avg.toFixed(1).padStart(4, '0');
	dom.das.great.textContent = game.data.das.great.toString().padStart(3, '0');
	dom.das.ok.textContent = game.data.das.ok.toString().padStart(3, '0');
	dom.das.bad.textContent = game.data.das.bad.toString().padStart(3, '0');

	// clear
	dom.das.ctx.clear();

	pixel_size = 4;
	max_pixels = Math.floor(dom.das.ctx.canvas.width / (pixel_size + 1));
	cur_x = 0;
	to_draw = game.pieces.slice(-1 * max_pixels);

	for (let idx = to_draw.length; idx--;) {
		const
			das = to_draw[idx].cur_piece_das,
			color = DAS_COLORS[ DAS_THRESHOLDS[das] ];

		dom.das.ctx.fillStyle = color;
		dom.das.ctx.fillRect(
			idx * (pixel_size + 1),
			(16 - das) * pixel_size,
			pixel_size,
			pixel_size
		);
	}
}