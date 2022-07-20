
let graphEl = null
let iconSize = 48 // 64
let iconHalfSize = 24 // 32

function dpi(s) {
	return Math.round(parseFloat(s)*72)
}

function setPosition(el, x, y) {
	el.setAttribute('x', x+'px')
	el.setAttribute('y', y+'px')
}

function getPath(coords) {
	let d = ''
	coords.forEach((c, i) => {
		d += (i%2 == 1) ? ',' : (i === 0) ? 'M' : (i === 2) ? 'C' : ' '
		d += dpi(c)
	})
	return d
}

function setCoords(el, coords) {
	el.setAttribute('d', getPath(coords))
}

const icons = {
	txt: 'icons/text-x-generic.svg',
	tex: 'icons/x-office-document.svg',
	html: 'icons/text-html.svg',
	css: 'icons/text-css.svg',
	svg: 'icons/x-office-drawing.svg',
	pdf: 'icons/gnome-mime-application-pdf.svg',
	jpg: 'icons/image-jpeg.svg',
	jpeg: 'icons/image-jpeg.svg',
	png: 'icons/image-png.svg',
	js: 'icons/text-x-script.svg',
	java: 'icons/text-x-java.svg',
	py: 'icons/text-x-python.svg',
	gifc: 'icons/image-gifc.svg',
}

function iconFile(name) {
	let suffix = name.replace(/^.*\./, '')
	return icons[suffix] || 'icons/text-x-preview.svg'
}

function imageElement(id) {
	let elem = document.getElementById(id)
	return elem && elem.getElementsByTagName('image')[0]
}
function textElement(id) {
	let elem = document.getElementById(id)
	return elem && elem.getElementsByTagName('text')[0]
}
function selRectElement(id) {
	let elem = document.getElementById(id)
	return elem && elem.getElementsByTagName('rect')[0]
}

function selectNode(id) {
	let elem = textElement(id)
	if (! elem) {
		console.warn(`selectNode ${id} NO TEXT - ${graph.nodes[id].tag}`)
		return
	}

	let rect = selRectElement(id)
	if (! rect) {
		rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
		elem.parentNode.insertBefore(rect, elem)
	}

	let bounds = elem.getBBox()
	rect.setAttribute('x', bounds.x - 2)
	rect.setAttribute('y', bounds.y - 2)
	rect.setAttribute('width', bounds.width + 4)
	rect.setAttribute('height', bounds.height + 4)
	rect.setAttribute('fill', 'yellow')
	rect.setAttribute('rx', 4)
	// if (elem.hasAttribute('transform)) {
	// 	sel.setAttribute('transform, elem.getAttribute('transform))
	// }

	anime({
		targets: rect,
		opacity: 1,
	})
}

function reselectNode(id, x, y) {
	let rect = selRectElement(id)
	if (!rect) {
		console.warn(`reselectNode ${id} NO RECT - ${graph.nodes[id].tag}`, bounds)
		selectNode(id)
		return
	}

	let elem = textElement(id)
	if (! elem) {
		console.warn(`reselectNode ${id} NO TEXT - ${graph.nodes[id].tag}`)
		return
	}
	let bounds = elem.getBBox()	// the text element has not been moved yet
	bounds.x = x - bounds.width/2
	bounds.y = y - bounds.height/2 - 4	// I don't know why, but we need this -4
	anime({
		targets: rect,
		x: bounds.x - 2,
		y: bounds.y - 2,
		width: bounds.width + 4,
		height: bounds.height + 4,
		easing: 'easeInOutCubic',
	})
}

function deselectNode(id) {
	let rect = selRectElement(id)
	if (rect) {
		anime({
			targets: rect,
			opacity: 0,
			complete: () => rect.remove()
		})
	} else
		console.warn(`deselectNode ${id} NO RECT - ${graph.nodes[id].tag}`)
}

function dummy(event){
	console.log("dummy text")
}

function createNode(id, x, y, w, h, label) {
	let node = graph.nodes[id]
	if (! node) {
		console.warn(`createNode: node ${id} not found`)
		node = {}
	}

	let g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
	g.setAttribute('id', id)
	g.setAttribute('class', 'node')
	g.setAttribute('opacity', 0)
	
	let img = document.createElementNS('http://www.w3.org/2000/svg', 'image')
	g.appendChild(img)
	img.setAttribute('href', iconFile(node.target))
	img.setAttribute('width', iconSize + 'px')
	img.setAttribute('height', iconSize + 'px')
	img.setAttribute('preserveAspectRatio', 'xMinYMin meet')
	setPosition(img, dpi(x) - iconHalfSize, dpi(y) - iconHalfSize)

	let txt = document.createElementNS('http://www.w3.org/2000/svg', 'text')
	g.appendChild(txt)
	txt.setAttribute('text-anchor', 'middle')
	txt.setAttribute('font-family', 'Helvetica,sans-Serif')
	txt.setAttribute('font-size', '12px')
	setPosition(txt, dpi(x), dpi(y) + iconHalfSize + 10)
	txt.appendChild(document.createTextNode(label))

	if (node.isSelected)
		selectNode(id)

	graphEl.appendChild(g)
	anime({
		targets: g,
		opacity: 1,
		easing: 'easeInCubic',
		duration: 500,
	})
}

let edgeStyles = {
	default: 	['black', 'url(#arrow)'],
	manual: 	['lightgrey', 'url(#manualarrow)'],
	stale: 		['red', 'url(#stalearrow)'],
	morph: 		['blue'],
	copy: 		['green', 'url(#copyarrow)',  {'stroke-dasharray': '3, 3'}],
}

function setEdgeStyle(edge, path) {
	let style = 'default'

	if (edge) {
		let isManual = edge.update_time > 1e+300
		let isMorph = edge.morph
		let isCopy = edge.copy
		let isStale = edge.parent_version && graph.nodes[edge.source].version && edge.parent_version !== graph.nodes[edge.source].version

		if (isManual)
			style = 'manual'
		else if (isStale)
			style = 'stale'
		else if (isMorph)
			style = 'morph'
		else if (isCopy)
			style = 'copy'
	} else
		console.warn(`setEdgeStyle: unexpected null edge for SVG element ${path}`)

	let [color, arrow, options] = edgeStyles[style]
	path.setAttribute('stroke', color)
	if (arrow)
		path.setAttribute('marker-end', arrow)
	if (options)
		for (let opt in options)
			path.setAttribute(opt, options[opt])
}

function createEdge(id, coords) {
	let edge = graph.edges[id]
	if (! edge) {
		console.warn(`createEdge: edge ${id} not found`)
		edge = {}
	}

	let g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
	g.setAttribute('id', id)
	g.setAttribute('class', 'edge')
	g.setAttribute('opacity', 0)

	let path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
	g.appendChild(path)
	path.setAttribute('fill', 'none')
	setEdgeStyle(edge, path)
	setCoords(path, coords)

	graphEl.appendChild(g)
	anime({
		targets: g,
		opacity: 1,
		easing: 'easeInCubic',
		duration: 500,
	})
}

function removeNode(id) {
	let node = document.getElementById(id)
	if (node) {
		anime({
			targets: node,
			opacity: 0,
			easing: 'easeOutCubic',
			complete: () => node.remove()
		})
	}
}

function removeEdge(id) {
	let edge = document.getElementById(id)
	if (edge) {
		anime({
			targets: edge,
			opacity: 0,
			easing: 'easeOutCubic',
			complete: () => edge.remove()
		})
	}
}

function isCollapsedMorph(id) {
	let morph = graph.morphs[id.replace('n', 'g')]
	return morph && morph.collapsed
}

let oldNodeIds = []
let newNodeIds = []
function updateNode(id, x, y, w, h, label) {
	newNodeIds.push(id)
	if (oldNodeIds.indexOf(id) < 0) {
		console.log(`updateNode: create new node ${id} - ${label}`)
		createNode(id, x, y, w, h, label)
	} else {
		console.log(`updateNode: update existing node ${id} - ${label}`)
		let node = graph.nodes[id]
		let el = document.getElementById(id)

		// Animate image to new position
		let img = imageElement(id)
		// setPosition(img, dpi(x) - 32, dpi(y) - 32)
		anime({
			targets: img,
			x: dpi(x) - iconHalfSize,
			y: dpi(y) - iconHalfSize,
			easing: 'easeInOutCubic',
		})

		// Animate text to new position
		let txt = textElement(id)
		// setPosition(txt, dpi(x), dpi(y) + 42)
		anime({
			targets: txt,
			x: dpi(x),
			y: dpi(y) + iconHalfSize + 10,
			easing: 'easeInOutCubic',
		})

		// Hack morphs to display gifc icon
		if (isCollapsedMorph(id)) {
			img.setAttribute('href', 'icons/image-gifc.svg')
			label = label.replace(/\.[^.]*$/, '.gifc')
		} else {
			console.log("this node here")
			console.log(node)
			img.setAttribute('href', iconFile(node.target))
		}

		// Change label
		let text = txt.firstChild	// the text node itself
		if (label !== text.nodeValue)
			text.replaceWith(label)

		// Animate selection appearance/disappearance/move
		let sel = selRectElement(id)
		if (sel) {
			if (node.isSelected)
				reselectNode(id, dpi(x), dpi(y) + iconHalfSize + 10)	// stays selected
			else
				deselectNode(id)	// becomes deselected
		} else {
			if (node.isSelected)
				selectNode(id)		// becomes selected
		}
	}
}

let oldEdgeIds = []
let newEdgeIds = []
function updateEdge(id, coords) {
	newEdgeIds.push(id)
	if (oldEdgeIds.indexOf(id) < 0) {
		createEdge(id, coords)
	} else {
		let el = document.getElementById(id)

		let path = el.childNodes[0]
		// setCoords(path, coords)

		// If the new coordinates have more point,
		// we extend the old list of points so the transition is smooth
		let oldD = path.getAttribute('d')
		let oldCoords = oldD.trim().split(/C| /)
		if (coords.length > oldCoords.length*2) {
			let tail = ' '+oldCoords[oldCoords.length-1]
			for(let i = oldCoords.length; i < coords.length/2; i++)
				oldD += tail
			path.setAttribute('d', oldD)
		}

		setEdgeStyle(graph.edges[id], path)

		anime({
			targets: path,
			d: getPath(coords),
			easing: 'easeInOutCubic',
		})
	}
}

function createMorph(id, minX, minY, maxX, maxY) {
	return
	let rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
	rect.setAttribute('id', id)
	rect.setAttribute('fill', 'none')
	rect.setAttribute('stroke', 'blue')
	rect.setAttribute('x', minX - iconHalfSize)
	rect.setAttribute('y', minY - iconHalfSize)
	rect.setAttribute('width', maxX - minX)
	rect.setAttribute('height', maxY - minY)
	rect.setAttribute('rx', 5)
	rect.setAttribute('opacity', 0)

	graphEl.appendChild(rect)

	anime({
		targets: rect,
		opacity: 1,
		easing: 'easeInCubic',
		duration: 500,
	})
}

let oldMorphIds = []
let newMorphIds = []
function updateMorph(id, minX, minY, maxX, maxY) {
	return
	newMorphIds.push(id)
	if (oldMorphIds.indexOf(id) < 0) {
		createMorph(id, minX, minY, maxX, maxY)
	} else {
		let rect = document.getElementById(id)
		anime({
			targets: rect,
			x: minX - iconHalfSize,
			y: minY - iconHalfSize,
			width: maxX - minX,
			height: maxY - minY,
			easing: 'easeInOutCubic',
		})
	}
}

function removeMorph(id) {
	return
	let rect = document.getElementById(id)
	if (rect) {
		anime({
			targets: rect,
			opacity: 0,
			easing: 'easeOutCubic'
		})
	}
}

function parseGraph(s) {
	console.log("parse")
	console.log(s)
	let nodeCoords = {}

	s.split('\n').forEach(l => {
		let line = l.split(' ')
		switch(line[0]) {
			case 'graph':
				break
			case 'node':
				let id = line[1]
				let x = line[2], y = line[3]
				let w = line[4], h = line[5]
				let label = line[6]
				if (line[6].match(/^"/))
					label = l.match(/"[^"]*"/)[0].slice(1, -1)
				updateNode(id, x, y, w, h, label)
				nodeCoords[id] = {x: dpi(x), y: dpi(y), w: dpi(w), h: dpi(h)}
				break
			case 'edge':
				let from = line[1], to = line[2]
				let coords = line.slice(4, 4 + 2*parseInt(line[3]))
				updateEdge(from+'_'+to, coords)
				break
			case 'stop':
				break
		}
	})

	for (let g in graph.morphs) {
		let group = graph.morphs[g]
		let minX = 10000, maxX = -10000, minY = 10000, maxY = -10000
		if (group.collapsed) {
			let coords = nodeCoords[g.replace('g', 'n')]
			minX = coords.x
			minY = coords.y
			maxX = coords.x + coords.w
			maxY = coords.y + coords.h
		} else {
			group.nodes.forEach(n => {
				let coords = nodeCoords[n]
				minX = Math.min(minX, coords.x)
				maxX = Math.max(maxX, coords.x + coords.w)
				minY = Math.min(minY, coords.y)
				maxY = Math.max(maxY, coords.y + coords.h)
			})
		}
		minX -= 5; maxX += 5; minY -= 5; maxY += 5
		updateMorph(g, minX, minY, maxX, maxY)
	}
}

function updateGraph(s) {
	oldNodeIds = newNodeIds
	newNodeIds = []

	oldEdgeIds = newEdgeIds
	newEdgeIds = []

	oldMorphIds = newMorphIds
	newMorphIds = []

	parseGraph(s)

	oldNodeIds.forEach(id => {
		if (newNodeIds.indexOf(id) === -1)
			removeNode(id)
	})

	oldEdgeIds.forEach(id => {
		if (newEdgeIds.indexOf(id) === -1)
			removeEdge(id)
	})

	oldMorphIds.forEach(id => {
		if (newMorphIds.indexOf(id) === -1)
			removeMorph(id)
	})
}

//To move nodes with the mouse
//https://www.petercollingridge.co.uk/tutorials/svg/interactive/dragging/
function makeDraggable(event) {
	var svg = event.target
	

    var selectedElement = false;


	svg.addEventListener('mousedown', startDrag);
	svg.addEventListener('mousemove', drag);
	svg.addEventListener('mouseup', endDrag);
	svg.addEventListener('mouseleave', endDrag);
	
	

	    function getMousePosition(event) {
	      var CTM = svg.getScreenCTM();
	      return {
		x: (evt.clientX - CTM.e) / CTM.a,
		y: (evt.clientY - CTM.f) / CTM.d
	      };
	    }


	
	function startDrag(evt) {
	//
	    selectedElement = evt.target;
	}
	
	function drag(event) {
		if (selectedElement) {
		    event.preventDefault();
		    var coord = getMousePosition(event);
		    selectedElement.setAttributeNS(null, "x", coord.x);
		    selectedElement.setAttributeNS(null, "y", coord.y);
		}
	}
	
	function endDrag(event) {
		selectedElement = null;
	}
	
	
}


