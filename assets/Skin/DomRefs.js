// Sort of like a pageObject to have quick references to the things that matter

class DomRefs {
	constructor(doc) {
		// store refs by component
		this.tetris_rate = doc.querySelector('#tetris_rate .content');

		this.burn = doc.querySelector('#burn .content');

		this.level = doc.querySelector('#level .content');

		this.lines = doc.querySelector('#lines .content');


		// =====================

		const droughts = doc.querySelector('#droughts');

		this.droughts = {
			num: droughts.querySelector('.header .count'),
			cur: {
				gauge: droughts.querySelector('.hgauge.current .value'),
				value: droughts.querySelector('.hgauge.current .gauge span')
			},
			max: {
				gauge: droughts.querySelector('.hgauge.max .value'),
				value: droughts.querySelector('.hgauge.max .gauge span')
			},
		};

		// =====================

		const score = doc.querySelector('#score');

		this.score = {
			current:    score.querySelector('.content .running .value'),
			transition: score.querySelector('.content .transition .value'),
		};

		// =====================

		const das = doc.querySelector('#das');

		this.das = {
			cur:   das.querySelector('.cur .count'),
			avg:   das.querySelector('.avg .count'),
			great: das.querySelector('.great .count'),
			ok:    das.querySelector('.ok .count'),
			bad:   das.querySelector('.bad .count'),
			ctx:   das.querySelector('.content canvas').getContext('2d'),
		};

		// =====================

		const lines_stats = doc.querySelector('#lines_stats');

		this.lines = {
			count: lines_stats.querySelector('.header .total_count'),
		};

		[
			'singles',
			'doubles',
			'triples',
			'tetris'
		]
		.forEach(category => {
			const row = lines_stats.querySelector(`tr.${category}`);

			this.lines[category] = {
				count:   row.querySelector('.count'),
				lines:   row.querySelector('.line_count'),
				percent: row.querySelector('.percent'),
			}
		});

		// =====================

		const points = doc.querySelector('#lines_stats');

		this.points = {
			count: lines_stats.querySelector('.header .total_count'),
		};

		[
			'down',
			'singles',
			'doubles',
			'triples',
			'tetris'
		]
		.forEach(category => {
			const row = lines_stats.querySelector(`tr.${category}`);

			this.points[category] = {
				count:   row.querySelector('.count'),
				percent: row.querySelector('.percent'),
			}
		});

		// =====================

		this.pieces = {};

		PIECES.forEach(name => {
			const piece_row = doc.querySelector(`#piece_stats .piece.${name}`);

			this.pieces[name] = {
				count:   piece_row.querySelector('.count'),
				drought: piece_row.querySelector('.drought'),
				percent: piece_row.querySelector('.percent span'),
				ctx:     piece_row.querySelector('canvas').getContext('2d')
			};
		});
	}
}