<template>
	<table class="table editable-datagrid">
		<thead>
			<tr>
				<th>Subject</th>
				<th>Predicate</th>
				<th>Object</th>
			</tr>
		</thead>
		<tbody>
			<tr
				v-if="editableMode"
				is="editable-data-grid-add"
				:columns="mapping.columns"
				:empty-columns-left="mapping.columns.indexOf('subject') == -1 ? 1 : 0"
				:empty-columns-right="mapping.columns.indexOf('object') == -1 ? 1 : 0"
			></tr>
			<tr v-for="(uuid, row) in rows | filterBy filterByCallback | orderBy orderByCallback" 
				is="editable-data-grid-row"
				:columns="mapping.columns"
				:uuid="uuid"
				:row="row"
				:original-row="originalRows[uuid]"
				:template="rowTemplate"
				:editable-mode="editableMode"
			></tr>
		</tbody>
	</table>
</template>



<script>
import Vue from 'vue'
import Utils from './../utils.js'
import Row from './editable-data-grid/row.vue'
import Add from './editable-data-grid/add.vue'

var newRowsCounter = 0

export default {
	components: {
		'editable-data-grid-row': Row,
		'editable-data-grid-add': Add
	},
	props: {
		filterString: String,
		mapping: Object,
		data: {
			coerce(dataArray) {
				return Utils.createUuidList(dataArray)
			}
		},
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		},
		rowTemplate: {
			type: String,
			defualt: 'default',
			required: false
		}
	},
	data: function () {
		var originalData = _.deepClone(this.data)

		return {
			columns: this.columns,
			originalData:  originalData,
			originalRows: this.computeRows(originalData)
		}
	},
	events: {
		addRow (newRow) {
			Vue.set(this.data, 'new-' + newRowsCounter + '-' + Utils.uuid(), this.mapping.create(newRow))
			newRowsCounter += 1
		},
		updateRow (uuid, updatedRow) {
			Vue.set(this.data, uuid, this.mapping.update(this.data[uuid], updatedRow)) 	
		},
		removeRow (uuid) {
			Vue.delete(this.data, uuid)
		},    
	},  
	computed: {
		rows() {
			return this.computeRows(this.data)
		},
		// Returns list of added data instances
		addedData() {
			return _.filter(
				this.data,
				function (entry, uuid) {
					return !_.has(this.originalData, uuid)
				},
				{ originalData: this.originalData }
			)
		},

		// Returns list of updated data instances
		updatedData() {
			return _.map(
				_.filterObject(
					this.data,
					function (entry, uuid) {
						return _.has(this.originalData, uuid) && !_.isEqual(this.originalData[uuid], entry)
					},
					{ data: this.data, originalData: this.originalData }
				),
				function (entry, uuid) {
					return {
						from: this.originalData[uuid],
						to: entry 
					} 
				},
				{ originalData: this.originalData }
			)
		},

		// Returns list of deleted data instances
		deletedData() {
			return _.filter(
				this.originalData,
				function (entry, uuid) {
					return !_.has(this.data, uuid)
				},
				{ data: this.data }
			)
		}
	},
	watch: {
		data: {
			// Using watcher to recompute rows. When rows is used as compute prop, updates doesn't work.
			handler () {
				this.rows = this.computeRows()
			},
			deep: true
		}
	},
	methods: {
		// creates list of rows from list of data objects
		computeRows (data) {
			return _.mapObject(data, entry => this.mapping.read(entry), { data: data, mapping: this.mapping })
		},

		// Filters rows by chcking if they contain 'filterString'. If row is modified, it is never filtered out.
		filterByCallback (row) {
			if (this.filterString.trim() == '') {
				return true
			}

			// Always keep, if data is updated
			var uuid = row.$key
			if (!_.isEqual(this.data[uuid], this.originalData[uuid])) {
				return true
			} 

			// Filter out rows that doesn't contain 'filterString' as substring of any of its fields
			return _.some(
				row.$value,
				function (value) { return value.toLowerCase().indexOf(this.filterString.toLowerCase()) != -1 },
				{ filterString: this.filterString }
			)
		},

		// Provides ordering by 'metadata.isNew' DESC (new rows are always on top) and then 'predicate' ASC (a -> z)
		orderByCallback (a, b) {
			// New rows to the front
			if (a.$key.startsWith("new-") && !b.$key.startsWith("new-")) return -1
			if (!a.$key.startsWith("new-") && b.$key.startsWith("new-")) return 1
			if (a.$key.startsWith("new-") && b.$key.startsWith("new-")) {
				if (parseInt(a.$key.split('-')[1]) > parseInt(b.$key.split('-')[1])) return -1
				return 1
			}

			// Rest sort by UUID
			if (a.$key == b.$key) return 0
			return a.$key > b.$key ? 1 : -1
		}
	}
}
</script>
