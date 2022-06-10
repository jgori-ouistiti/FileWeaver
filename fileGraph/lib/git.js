
const fs = require('fs')
const path = require('path')
const { execFile } = require('child_process')

const params = require('../params.js')

function git2svg(filePath, cb) {

	if (params.mode === 'test') {
		// return fs.readFileSync('test/out.dot.svg', 'utf8')
		filePath = path.resolve('test/files/2053_4982370/main.tex')
	}

	let dir = path.dirname(filePath)

	params.git2dotArgs[0] = path.resolve(params.git2dot)

	let child = execFile('python', params.git2dotArgs, {
		cwd: dir,
	}, (error, stdout, stderr) => {
		if (error)
			console.error(error)
		if (stderr)
			console.warn(stderr)
		if (stdout)
			console.log(stdout)

		let svg = fs.readFileSync(path.join(dir, 'git.dot.svg'), 'utf8')
		cb(svg)
	})
}

module.exports = {
	git2svg
}
