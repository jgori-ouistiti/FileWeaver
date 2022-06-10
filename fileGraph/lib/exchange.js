
const fs = require('fs')
const chokidar = require('chokidar')

const params = require('../params')

const watcher = chokidar.watch(params.exchangePath)

function addMorph(graph, morphName, nodeName) {
	if (! graph.morphs[morphName])
		graph.morphs[morphName] = {nodes: [nodeName], collapsed: false}
	else
		graph.morphs[morphName].nodes.push(nodeName)
}

function parseNodeFlags(graph, id, node) {
	node.isSelected = false

	// process Copy flag
	let copyFlag = node.flags[1]
	if (copyFlag > 0) {
		graph.edges['n'+id+'_n'+copyFlag] = { source: 'n'+id, target: 'n'+copyFlag, copy: true}
		graph.nodes['n'+id].copyOf = 'n'+copyFlag
	}

	// process Morph flag
	let morphFlag = node.flags[2]
	switch (morphFlag) {
		case -2:
			node.morph = null
			break
		case -1:
			node.morph = { head: true, group: id}
			addMorph(graph, 'g'+id, 'n'+id)
			console.warn('morph head', id)
			break
		default:
			node.morph = { head: false, group: morphFlag}
			let morphName = 'g'+morphFlag
			let headName = 'n'+morphFlag
			let nodeName = 'n'+id
			addMorph(graph, morphName, nodeName)
			graph.edges[headName+'_'+nodeName] = { source: headName, target: nodeName, morph: morphName}
			console.warn(`morph group for ${id} is ${morphFlag}`)
	}
}

function removeNode(graph, node) {
	console.log(`   -> deleting node ${node.id} - ${node.tag}`)
	let nodeName = 'n'+ex.id

	delete graph.nodes[nodeName]

	for(let e in graph.edges) {
		let edge = graph.edges[e]
		if (nodeName === edge.source || nodeName === edge.target) {
			console.log(`   -> deleting edge ${edge.id}`)
			delete graph.edges[e]
		}
	}

	for (let g in graph.morphs) {
		let nodes = graph.morphs[g].nodes
		let i = nodes.indexOf(nodeName)
		if (i) {
			console.log(`   -> removing from morph ${g}`)
			nodes.splice(i, 1)
		}
		if (nodes.length === 0) {
			console.log(`   -> deleting morph ${g}`)
			delete graph.morphs[g]
		}
	}
}

function parseEdgeId(id) {
	return id.split('#').map(i => i.replace('.0', ''))
}

function parseGraphAction(graph, ex) {
	let node, nodeName, edge, edgeName, from, to
	switch (ex.action) {
		case 'add': 
			console.log(`adding node ${ex.id} - ${ex.vpdic.tag}`)
			nodeName = 'n'+ex.id
			if (graph.nodes[nodeName])
				console.error(`parseGraphAction add node ${nodeName}: node exists`)
			ex.vpdic.linkname = ex.linkname
			graph.nodes[nodeName] = ex.vpdic
			parseNodeFlags(graph, ex.id, ex.vpdic)
			break
		case 'add_edge':
			;[from, to] = parseEdgeId(ex.id)

			console.log(`adding edge ${ex.id}`)
			edgeName = 'n'+from+'_n'+to
			if (graph.nodes[edgeName])
				console.error(`parseGraphAction add edge ${edgeName}: edge exists`)
			edge = graph.edges[edgeName] = ex.epdic
			edge.source = 'n'+from
			edge.target = 'n'+to
			break
		case 'update':
			console.log(`updating node ${ex.id} - ${ex.vpdic.tag}`)
			nodeName = 'n'+ex.id
			node = graph.nodes[nodeName]
			if (! node) {
				console.error(`update: node ${nodeName} does not exist`)
				return
			}
			if (ex.vpdic.status === 0)
				removeNode(graph, node)
			else {
				for (let p in ex.vpdic)
					node[p] = ex.vpdic[p]
				parseNodeFlags(graph, ex.id, node)
			}
			break
		case 'update_edge':
			console.log(`updating edge ${ex.id}`)
			;[from, to] = parseEdgeId(ex.id)
			edgeName = 'n'+from+'_n'+to
			edge = graph.edges[edgeName]
			if (! edge) {
				console.error(`update: edge ${edgeName} does not exist`)
				return
			}
			for (let p in ex.epdic)
				edge[p] = ex.epdic[p]
			break
		/* no delete node: update with status 0 instead
		case 'delete':
			console.log(`deleting node ${ex.id} - ${ex.vpdic.tag}`)
			nodeName = 'n'+ex.id
			node = graph.nodes[nodeName]
			if (! node) {
				console.error(`delete: node ${nodeName} does not exist`)
				return
			}
			delete graph.nodes[nodeName]
			break
		*/
		case 'delete_edge':
			console.log(`deleting edge ${ex.id}`)
			;[from, to] = parseEdgeId(ex.id)
			edgeName = 'n'+from+'_n'+to
			edge = graph.edges[edgeName]
			if (! edge) {
				console.error(`delete: edge ${edgeName} does not exist`)
				return
			}
			delete graph.edges[edgeName]
			break
		default:
			console.warn(`unknown action ${ex.action}`)
	}
}

function parseVizAction(graph, ex) {
	if (! ex.linkname || ex.linkname.length === 0)
		return

	let first = true
	ex.linkname.forEach(link => {
		for (let n in graph.nodes) {
			let node = graph.nodes[n]
			if (node.linkname === link) {
				// deselect any selected nodes only if the selection changes
				if (first) {
					for (let n in graph.nodes)
						graph.nodes[n].isSelected = false
					first = false					
				}

				node.isSelected = true
				console.log(`selecting link ${link} -> node ${n}`)
				return
			}
		}
		console.log(`selecting unknown link ${link} `)
	})
}

function parseExchange(graph, ex) {
	switch(ex.type) {
		case 'G': parseGraphAction(graph, ex); break
		case 'V': parseVizAction(graph, ex); break
	}
}

function processExchange(graph, ex) {
	// console.log(ex)
	try {
		let cmd = JSON.parse(ex)
		parseExchange(graph, cmd)
	} catch(err) {
		console.error('Error parsing exchange file: ', err)
	}
}

function processChange(path, graph, cb) {
	let ex = fs.readFileSync(path, 'utf8')
	if (ex === '') {
		// console.log('watchExchange: empty string')
		return
	}
	fs.truncateSync(path)

	let exlist = ex.split('}{')
	if (exlist.length === 1) 
		processExchange(graph, ex)
	else
		exlist.forEach((ex, i) => {
			if (i === 0)
				ex += '}'
			else if (i === exlist.length-1)
				ex = '{'+ex
			else
				ex = '{'+ex+'}'
			processExchange(graph, ex)
		})

	cb(graph)
}

let paused = false
let catchUp = null
function pause() {
	paused = true
}
function resume() {
	paused = false
	if (catchUp) {
		processChange(...catchUp)
		catchUp = null
	}
}

function watch(graph, cb) {
	watcher.on('change', (path, stats) => {
		if (paused) {
			catchUp = [path, graph, cb]
			return
		}
		processChange(path, graph, cb)
	})
}

module.exports = {
	watch,
	pause,
	resume,
}
