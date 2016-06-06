import Vue from 'vue'
import Utils from './utils.js'
import Resource from './components/resource.vue' 
import EditableDataGrid from './components/editable-data-grid.vue'

Vue.component('resource', Resource);
//Vue.component('editable-data-grid', EditableDataGrid);

new Vue({
	el: '#v-app'//,
//	data: {
//		searchQuery: '',
//		gridColumns: ['name', 'power'],
//		gridData: Utils.createUuidList([
//			// NOTE: All attributes must be string for now!
//			{ name: 'Chuck Norris', power: "Infinity" },
//			{ name: 'Bruce Lee', power: "9000" },
//			{ name: 'Jackie Chan', power: "7000" },
//			{ name: 'Jet Li', power: "8000" }
//		])
//	}
})