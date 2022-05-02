
const backend = require('../lib/backend')

backend.start(data => console.log('backend says: '+data))

let i = 0
setInterval(() => {
	i++
	backend.send(`toto ${i}`)
	if (i === 20)
		backend.close()
}, 20)