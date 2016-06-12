<template>
	<table class="table">
		<thead>
			<!-- Original <th>'s with ordering -->
			<!--tr>
				<th>#</th>
				<th v-for="key in columns"
					@click="sortBy(key)"
					:class="{active: sortKey == key}">
					{{key | capitalize}}
					<span class="arrow"
						:class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
					</span>
				</th>
			</tr-->
			<tr>
				<th>Predicate</th>
				<th>Object</th>
			</tr>
		</thead>
		<tbody>
			<tr v-for="
					(uuid, row) in rows
					| filterBy filterString
					| orderBy sortKey sortOrders[sortKey]"
				is="editable-data-grid-row"
				:columns="mapping.columns"
				:uuid="uuid"
				:row="row"
			></tr>
		</tbody>
		<tfoot is="editable-data-grid-add" :columns="mapping.columns"></tfoot>
	</table>

	<h4>Added:</h4>
	<pre>{{ addedData | json }}</pre>
	<h4>Updated:</h4>
	<pre>{{ updatedData | json }}</pre>
	<h4>Deleted:</h4>	
	<pre>{{ deletedData | json }}</pre>

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
		}//,
		//filterKey: String // TODO
	},
	data: function () {
//		var sortOrders = {}
//		var columns = ["subject", "predicate", "object"] 
//		columns.forEach(function (key) {
//			sortOrders[key] = 1
//		})

		return {
//			sortKey: '',
//			filterKey: '',
//			sortOrders: sortOrders,
			rows: this.computeRows(),
			originalData: _.deepClone(this.data),
			columns: this.columns
		}
	},
	events: {
		addRow (newRow) {
			Vue.set(this.data, Utils.uuid(), this.mapping.create(newRow))
		},
		updateRow (uuid, updatedRow) {
			Vue.set(this.data, uuid, this.mapping.update(this.data[uuid], updatedRow)) 	
		},
		removeRow (uuid) {
			Vue.delete(this.data, uuid)
		},    
	},  
	computed: {
		addedData() {
			return _.filter(
				this.data,
				function (entry, uuid) {
					return !_.has(this.originalData, uuid)
				},
				{ originalData: this.originalData }
			)
		},
		updatedData() {
			return _.filter(
				this.data,
				function (entry, uuid) {
					return _.has(this.originalData, uuid) && !_.isEqual(this.originalData[uuid], entry)
				},
				{ data: this.data, originalData: this.originalData }
			)
		},
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
		computeRows () {
			return _.mapObject(this.data, entry => this.mapping.read(entry), { mapping: this.mapping })
		}//,
//		sortBy: function (key) {
//			this.sortKey = key
//			this.sortOrders[key] = this.sortOrders[key] * -1
//		}
	}
}
</script>
