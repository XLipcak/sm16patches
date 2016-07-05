<template>
	<table class="table">
		<thead>
			<tr>
				<th>Subject</th>
				<th>Predicate</th>
				<th>Object</th>
			</tr>
		</thead>
		<tbody>
			<tr is="editable-data-grid-add" v-if="editableMode" :columns="mapping.columns"></tr><!-- orderBy 'metaData.isNew' -->
			<tr v-for="(uuid, row) in rows | filterBy filterString | orderBy defaultOrder" 
				is="editable-data-grid-row"
				:columns="mapping.columns"
				:uuid="uuid"
				:row="row"
				:template="rowTemplate"
				:editable-mode="editableMode"
			></tr>
		</tbody>
	</table>
</template>



<!-- ORIGINAL TABLE TEMPLATE -->
<!--
	<table class="table">
		<tbody>
			{% for subject, predicate, object in rdfGraph.triples( (URIRef(url), None, None) ) %}
				<tr>
					<td class="first"><a href="{{ predicate }}">{{ predicate }}</a></td>
					{% if isinstance(object, URIRef) %}
						<td class="second">
							<p class="break">
								<a href="{{object}}">{{ object }}</a>
							</p>
						</td>
					{% else %}
						<td class="second">
							<p class="break">
								{{ object }}
							</p>
						</td>
					{% end %}
				</tr>
			{% end %}						
		</tbody>
	</table>
-->



<script>
import Vue from 'vue'
import Utils from './../utils.js'
import Row from './editable-data-grid/row.vue'
import Add from './editable-data-grid/add.vue'

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
		return {
			rows: this.computeRows(),
			originalData: _.deepClone(this.data),
			columns: this.columns
		}
	},
	events: {
		addRow (newRow) {
			Vue.set(this.data, 'new-' + Utils.uuid(), this.mapping.create(newRow))
		},
		updateRow (uuid, updatedRow) {
			Vue.set(this.data, uuid, this.mapping.update(this.data[uuid], updatedRow)) 	
		},
		removeRow (uuid) {
			Vue.delete(this.data, uuid)
		},    
	},  
	computed: {
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
		computeRows () {
			return _.mapObject(this.data, entry => this.mapping.read(entry), { mapping: this.mapping })
		},

		// Provides ordering by 'metadata.isNew' DESC (new rows are always on top) and then 'predicate' ASC (a -> z)
		defaultOrder (a, b) {
			// New rows to the front
			if (a.$key.startsWith("new-") && !b.$key.startsWith("new-")) return -1
			if (!a.$key.startsWith("new-") && b.$key.startsWith("new-")) return 1

			// Rest alphabetically by predicate
			if (a.$value.predicate == b.$value.predicate) return 0
			return a.$value.predicate > b.$value.predicate ? 1 : -1
		}
	}
}
</script>
