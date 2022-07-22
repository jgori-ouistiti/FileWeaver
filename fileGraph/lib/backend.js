
const { spawn } = require('child_process')
const params = require('../params')

let backend = null
let callback = null

function start(cb) {
	//callback = cb
	//backend = spawn('python3', ['-u', params.backendPath])
	//backend.stdout.on('data', cb)
	// backend.stdout.on('data', (data) => {
//   console.log(`stdout: ${data}`);
// });
	backend.on('close', () => {
		console.log('backend closed')
		backend = null
	})
	console.log('backend started')
}

function send(...args) {
	if (! backend) {
		console.error('backend.send: backend closed')
		return
	}
	console.log('to backend: '+args.join(','))
	backend.stdin.write(args.join(',')+'\n')
}

function close() {
	if (backend) {
		backend.stdin.end()
		backend = null
	}
}

function restart() {
	if (backend)
		close()
	start(callback)
}

module.exports = {
	start,
	send,
	close,
	restart,
}
