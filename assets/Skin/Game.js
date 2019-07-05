class Game {
	constructor() {
		// will store all pieces that have been played in the game
		this.pieces = [];
		this.lines = [];
		this.last_event = null;

		this.stats = {
			das: {
				great: 0,
				ok:    0,
				bad:   0
			},
			pieces: {
			}
		}

		PIECES.forEach(name => {
			this.stats.pieces[name] = {
				name,
				count:   0,
				percent: 0,
				drought: 0
			}
		});
	}
}