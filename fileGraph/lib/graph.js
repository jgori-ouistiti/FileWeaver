
const parseString = require('xml2js').parseString
const fs = require('fs')
const { execFile } = require('child_process')

// Create a graph from a string in the graphML XML format
function parseGraphML(gml) {
	let keys = {
		graph: {},
		node: {},
		edge: {},
	}

	let graph = {
		nodes: {},
		edges: {},
		morphs: {},
	}

	gml.graphml.key.forEach(k => {
		keys[k.$.for][k.$.id] = {
			name: k.$['attr.name'],
			type: k.$['attr.type'],
		}
	})

	gml.graphml.graph[0].node.forEach(n => {
		let id = n.$.id
		let node = {}
		n.data.forEach(d => {
			let key = d.$.key
			let val = d['_']
			node[keys.node[key].name] = val
		})
		graph.nodes[id] = node

		// TODO parse morphgroups and copies
	})

	gml.graphml.graph[0].edge.forEach(e => {
		let id = e.$.source+'_'+e.$.target //e.$.id
		let edge = {
			source: e.$.source,
			target: e.$.target,
		}
		e.data.forEach(d => {
			let key = d.$.key
			let val = d['_']
			edge[keys.edge[key].name] = val
		})
		graph.edges[id] = edge
	})
	
	return graph
}

function includeNode(graph, node) {
	if (! node.morph)
		return true
	if (node.morph.head)
		return true
	let group = graph.morphs['g'+node.morph.group]
	return ! group.collapsed
}

function includeEdge(graph, edge) {
	if (! edge.morph)
		return true
	return ! graph.morphs[edge.morph].collapsed
}

// return the head of the morph if nodeName is in a morph that is collapsed
function adjustEdgeEnd(graph, nodeName) {
	let node = graph.nodes[nodeName]
	if (! node.morph)
		return nodeName
	let groupName = 'g'+node.morph.group
	if (graph.morphs[groupName].collapsed)
		return 'n'+node.morph.group
	return nodeName
}

// Layout a graph with the `dot` graph layout program.
// The returned value is the output of dot.
function toDot(graph) {
	let dot = 'strict digraph {'
	dot += '\n    rankdir = LR; '
	dot += '\n    node [fontname=Helvetica image="document.png" shape=none height=1 imagepos=tc labelloc=b]'

	for (let g in graph.morphs) {
		let group = graph.morphs[g]
		if (group.collapsed)
			dot += `\n    subgraph cluster${g} {${g.replace('g', 'n')}}`
		else
			dot += `\n    subgraph cluster${g} {${group.nodes.join('; ')}}`
	}

	for (let n in graph.nodes) {
		let node = graph.nodes[n]
		if (! includeNode(graph, node))
			continue
		if (node.tag !== 'NA')
			dot += `\n    ${n} [label = "${node.tag}"]`
		if (node.copyOf) {
			dot += `\n { rank = same; ${n}; ${node.copyOf}}`
		}
	}
	dot += '\n'

	for (let e in graph.edges) {
		let edge = graph.edges[e]
		if (! includeEdge(graph, edge))
			continue
		let src = adjustEdgeEnd(graph, edge.source)
		let dst = adjustEdgeEnd(graph, edge.target)
		// dot += `\n    "${graph.nodes[src].tag}" -> "${graph.nodes[dst].tag}"`
		dot += `\n    ${src}:e -> ${dst}`
	}

	dot += '\n}'

	return dot
}

// Parse the GraphML file `name` and call `cb` with the parsed graph
function parse(name, cb) {
	var src = name+'.graphml'
	var xml = fs.readFileSync(src, 'utf8')
	parseString(xml, function (err, res) {
		cb(parseGraphML(res))
	})
}

// Layout `graph` with dot and call `cb` with the resulting dot output
function layout(graph, cb) {
	let dot = toDot(graph)
	
	child = execFile('dot', ['-Tplain'], (error, stdout, stderr) => {
				if (error) {
					console.error('dot says: ', error)
					return
				}
				// console.log(dot)
				// console.log(stdout)
				cb(stdout)
			})
	child.stdin.write(dot)
	child.stdin.end()

/* SVG output
	svgchild = execFile('dot', ['-Tsvg'], (error, stdout, stderr) => {
				if (error) {
					console.error('dot -Tsvg says: ', error)
					return
				}
				fs.writeFileSync('graph.svg', stdout, 'utf8')
			})
	svgchild.stdin.write(dot)
	svgchild.stdin.end()
*/
}

module.exports = {
	parse,
	layout,
}
