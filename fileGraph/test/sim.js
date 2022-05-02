var fs = require('fs')

let single = false
let all = false
let file = 'exchange-log3.json'

function paceExchange(i) {
	if (i >= exchange.length) {
		console.log('DONE')
		return
	}

	// group a random number of operations in one batch, to simulate bursts
	let n = single ? 1 : all ? exchange.length : Math.round(Math.random()*3)+1
	let out = ''

	exchange.slice(i, i+n).forEach(ex => out += JSON.stringify(ex))
	console.log(`--- ${n} items\n`, out)

	fs.appendFileSync('exchange.json', out, 'utf8')
	setTimeout(() => paceExchange(i+n), 1000)
}

let args = process.argv.slice(2)
while (args.length >= 1) {
	if (args[0] === '-a')
		all = true
	else if (args[0] == '-1')
		single = true
	else
		file = args[0]
	args.shift()
}
console.log(single, all, file)

let exchange = fs.readFileSync(file, 'utf8').split('}{').map((ex, i, a) => {
	if (i === 0)
		return JSON.parse(ex+'}')
	if (i === a.length-1)
		return JSON.parse('{'+ex)
	return JSON.parse('{'+ex+'}')
})

paceExchange(0)
