
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
socket.addEventListener('message', onFrame);
/**/

fake_idx = 0
interval = setInterval(() => {onFrame(frames[fake_idx++])}, 16);

const
	fields = ['score', 'level', 'lines', 'cur_piece_das'],
	dom =    new DomRefs(document);

var
	game = null,
	last_valid_event = null;

function onFrame(event) {
	// validation
	if (!fields.every(field => event[field]) && game && game.started) {
		// could be pause?
		// could be score screen?
		// TODO: save previous game
		game = last_valid_event = null;
		return;
	}

	// transformation
	const transformed = {
		score:         parseInt(event.score, 10),
		lines:         parseInt(event.lines, 10),
		level:         parseInt(event.level, 10),
		cur_piece_das: parseInt(event.cur_piece_das, 10),
		cur_piece:     event.cur_piece,
		next_piece:    event.next_piece_das,
		stage: {
			num_blocks: event.stage[0],
			top_row:    event.stage[1][0].join('')
		}
	};

	let
		piece_entry =   false,
		cleared_lines = 0;

	if (transformed.stage.num_blocks % 2 == 1) return;

	if (!game) {
		game = new Game(transformed.level);
	}

	if (last_valid_event) {
		const 
			old_stage = last_valid_event.stage,
			new_stage = transformed.stage;


		if (new_stage.num_blocks > old_stage.num_blocks) {
			if (new_stage.num_blocks - old_stage.num_blocks != 4) {
				return;
			}
			else {
				piece_entry = true;
			}
		}
		else if (old_stage.num_blocks == new_stage.num_blocks) {
			return;
		}

		if (old_stage.top_row === new_stage.top_row) {
			return;
		}

		cleared_lines = event.lines - last_valid_event.lines;
	}
	else {
		if (transformed.stage.num_blocks % 4 === 0) {
			piece_entry = true;
		}		
	}

	last_valid_event = transformed;

	if (cleared_lines) {
		game.onLine(transformed);
		renderPiece();
	}
	else if (piece_entry) {
		game.onPiece(transformed);
		renderPiece();
	}
}


const line_categories = [
	[1, 'singles'],
	[2, 'doubles'],
	[3, 'triples'],
	[4, 'tetris']
];


function renderPiece() {
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

	dom.points.down.count.textContent = game.data.points.down.count.toString().padStart(6, '0');
	dom.points.down.percent.textContent = Math.round(game.data.points.down.percent * 100).toString().padStart(2, '0') + '%';


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