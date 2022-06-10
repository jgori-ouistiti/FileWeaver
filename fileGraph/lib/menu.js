

const StateMachine = require('lib/statemachine')

// menuInfo {
// 	menu: 	the context menu element
//	item: 	the context menu item element
//	cmd: 	the id attribute of the item, if any
// 	target: the graph element under the cursor when the menu was opened
// 	type: 	the type of the element (node/edge/graph)
// }

function getTarget(target) {
	while (target !== document) {
		if (target.classList.contains('node'))
			return [target, 'node']
		if (target.classList.contains('edge'))
			return [target, 'edge']
		if (target.classList.contains('graph'))
			return [target, 'graph']
		if (target.classList.contains('menu'))
			return [target, 'menu']
		target = target.parentNode
	}
	return [null, null]
}

function hasParentWithClass(e, c) {
	while(e && e !== document)
		if (e.classList && e.classList.contains(c))
			return true
		else
			e = e.parentNode
	return false
}

let context = {
	menuInfo: null,

	hasContextMenu(e) {
		let [target, type] = getTarget(e.target)
		if (type === 'menu')
			return false

		let menu = document.getElementById(type+'Menu')
		if (! menu) {
			console.warn(`no context menu ${type}Menu`)
			return false
		}
		this.menuInfo = {
			menu,
			target,
			type
		}
		return true
	},

	openContextMenu(e) {
		let info = this.menuInfo
		contextMenus[info.type].checkDisabled(info)
		info.menu.style.left = e.clientX+'px'
		info.menu.style.top  = e.clientY+'px'
		info.menu.style.display = 'block'
		info.menu.classList.add('display')

		global.exchange.pause()
	},

	executeContextMenu(e) {
		let info = this.menuInfo
		info.item = e.target
		let menu = contextMenus[info.type]
		let id = info.cmd = info.item.getAttribute('id')
		if (id && menu[id])
			menu[id](info)
		else
			menu.execute(info)
	},

	closeContextMenu(e) {
		let info = this.menuInfo
		info.menu.classList.remove('display')
		global.exchange.resume()
		this.menuInfo = null
	},

	onItem(e) {
		return hasParentWithClass(e.target, 'items')
	},
	onMenu(e) {
		return hasParentWithClass(e.target, 'menu')
	},
	hasNotMoved(e) {
		return !this.menuInfo.moved
	},

	onNode(e) {
		return hasParentWithClass(e.target, 'node')
	},

	clickNode(e) {
		clickCommands.clickNode(e)
	},
	dblclickNode(e) {
		clickCommands.dblclickNode(e)
	},
	clickGraph(e) {
		clickCommands.clickGraph(e)
	},

}

let sm = new StateMachine(context, {
	start: {
		on_contextmenu: 'hasContextMenu ? -> contextMenu',
		on_click: [
			'onNode ? clickNode',
			'clickGraph',
		],
		on_dblclick: 'onNode ? dblclickNode',
	},

	contextMenu: {
		enter: 'openContextMenu',
		exit: 'closeContextMenu',
		on_mouseup: [
			'onItem ? executeContextMenu -> start',
			'hasNotMoved ? ',
			'-> start'
		],
		on_mousemove: {
			action(e) { this.menuInfo.moved = true }
		},
		on_click: [
			'onItem ? executeContextMenu -> start',
			'-> start',
		],
		on_contextmenu: [
			'onMenu ? ',
			{
				action(e) {
					this.closeContextMenu(e)
					if (this.hasContextMenu(e))
						this.openContextMenu(e)
					else
						sm.currentState = sm.states.start	// HACK!
				}
			}
		]
	},
})

function processEvent(e) {
	if (sm.processEvent(e.type, e))
		e.preventDefault()
}

function initMenu() {
	document.addEventListener('contextmenu', processEvent)
	document.addEventListener('mousedown', processEvent)
	document.addEventListener('mousemove', processEvent)
	document.addEventListener('mouseup', processEvent)
	document.addEventListener('click', processEvent)
	document.addEventListener('dblclick', processEvent)
}
