
let git2dotArgs = [
	'git2dot.py',	// will be replaced by the path to the git2dot script, as specified in params.git2dot
	'-d', 'edge[dir="Forward"]',
	// '-d', 'rankdir=TB',	// for vertical layout
	'-w', '15',
	'--cnode', '[label="{label}", shape="note", color="darkgrey", fillcolor="bisque"]',
	'--mnode', '[label="{label}", shape="note", color="darkgrey", fillcolor="bisque"]', //, shape="component", color="#d3d3d3", style="bold"]',
	'-l', '%s|%cr', //'%h|%s|%cd|%cr',
	'--svg', 'git.dot',
]

let test = {
	mode: 'test',
	exchangePath: 'test/exchange.json',
	backendPath: 'test/backend_entry.py',
	git2dot: '../nautilusGit/git2dot.py',
	git2dotArgs,
}

let prod = {
	exchangePath: '/home/alexandre/Documents/StageM1/FileWeaver/exchange.json',
	backendPath: '/home/alexandre/Documents/StageM1/FileWeaver/fileGraph/test/backend_entry.py',
	git2dot: '../nautilusGit/git2dot.py',
	git2dotArgs,
}

let tp = {
	exchangePath: 'test/exchange.json',
	backendPath: '../../branch-JG/backend_entry.py',
}

// Set exports to proper configuration
// module.exports = test
module.exports = prod
// module.exports = tp
