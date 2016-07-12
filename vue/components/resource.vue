<template xmlns:v-on="http://www.w3.org/1999/xhtml">
	<h1>RDF</h1>
	<h2>About: <a href= "{{ url }}"> {{url}} </a> </h2>
	<br><br>
	<div class="form-group">
		<label for="searchText" style="font-size: 15pt;">Filter:</label>
		<input type="hidden" name="url" value="{{url}}" />
		<input v-model="searchString" id="searchText" name="searchText" placeholder="Search..." value="{{searchText}}" class="form-control" type="text" />
	</div>

	<ul class="nav nav-tabs">
		<li class="active"><a data-toggle="tab" href="#resource-as-subject">Resource as subject</a></li>
		<li><a data-toggle="tab" href="#resource-as-object">Resource as object</a></li>
	</ul>

	<div class="tab-content">
		<div id="resource-as-subject" class="tab-pane active">
			<editable-data-grid
				v-ref:data-grid-subject
				row-template="subject"
				:data="urlAsSubject.triples"
				:mapping="urlAsSubject.mapping"
				:filter-string="searchString"
				:editable-mode="isEditableMode"
			></editable-data-grid>
		</div>

		<div id="resource-as-object" class="tab-pane">
			<editable-data-grid
				v-ref:data-grid-object
				row-template="object"
				:data="urlAsObject.triples"
				:mapping="urlAsObject.mapping"
				:filter-string="searchString"
				:editable-mode="isEditableMode"
			></editable-data-grid>
		</div>
	</div>	

	<h3>Blank nodes</h3>
	<em>To be done.</em>

	<div class="footer navbar-fixed-bottom">
		<div class="panel panel-default panel-bottom">
			<div class="panel-body text-center">
				<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#patchModal">
					Submit Changes
				</button>
			</div>
		</div>	
	</div>

	<!-- Recorded chagnes Modal -->
	<div class="modal fade" id="patchModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog modal-recorded-changes" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel">Recorded changes</h4>
					<div>
						<span>
							Here you can take a look at the changes you've made. If these are as intended go on and submit your request!
						</span>
					</div>
				</div>
				<div class="modal-body">
					<h4>Triples where <a href="{{ url }}"> {{ url }} </a> is the subject:</h4>
					<table class="table recorded-changes">
						<tr>
							<th>Subject</th>
							<th>Predicate</th>
							<th>Object</th>
						</tr>

						<!-- Added -->
						<tr class="added" v-for="triple in $refs.dataGridSubject.addedData">
							<td>{{ triple.subject }}</td>
							<td>{{ triple.predicate }}</td>
							<td>{{ triple.object }}</td>
						</tr>

						<!-- Updated -->
						<tr class="updated" v-for="triple in $refs.dataGridSubject.updatedData">
							<td>{{ triple.to.subject }}</td>
							<td>{{ triple.to.predicate }}</td>
							<td>{{ triple.to.object }}</td>
						</tr>

						<!-- Deleted -->
						<tr class="deleted" v-for="triple in $refs.dataGridSubject.deletedData">
							<td>{{ triple.subject }}</td>
							<td>{{ triple.predicate }}</td>
							<td>{{ triple.object }}</td>
						</tr>
					</table>

					<h4>Triples where <a href="{{ url }}"> {{ url }} </a> is the object:</h4>
					<table class="table recorded-changes">
						<tr>
							<th>Subject</th>
							<th>Predicate</th>
							<th>Object</th>
						</tr>

						<!-- Added -->
						<tr class="added" v-for="triple in $refs.dataGridObject.addedData">
							<td>{{ triple.subject }}</td>
							<td>{{ triple.predicate }}</td>
							<td>{{ triple.object }}</td>
						</tr>

						<!-- Updated -->
						<tr class="updated" v-for="triple in $refs.dataGridObject.updatedData">
							<td>{{ triple.to.subject }}</td>
							<td>{{ triple.to.predicate }}</td>
							<td>{{ triple.to.object }}</td>
						</tr>

						<!-- Deleted -->
						<tr class="deleted" v-for="triple in $refs.dataGridObject.deletedData">
							<td>{{ triple.subject }}</td>
							<td>{{ triple.predicate }}</td>
							<td>{{ triple.object }}</td>
						</tr>
					</table>
				</div>
				<div class="modal-footer">
					<div class="text-center">
						<button id="submitPatch" type="button" class="btn btn-primary" v-on:click="postPatchRequest">Save Patch Request</button>
					</div>
				</div>
			</div>
		</div>
	</div>		

	<!-- Successful request Modal -->		
</template>



<script>
import Utils from './../utils.js'
import RdfTriple from './../model/rdf-triple.js'
import EditableDataGrid from './editable-data-grid.vue'

export default {
	components: {
		'editable-data-grid': EditableDataGrid
	},
	props: {
		jsonData: String,
		url: String,
		filename: String
	},
	data () {
		var jsonObject = JSON.parse(this.jsonData)
		this.filename = jsonObject.filename
		var triples = RdfTriple.arrayOfTriplesFromJson(jsonObject.data)
		var url = this.url

		return {
			isEditableMode: true,
			searchString: "",
			urlAsSubject: {
				triples: _.filter(triples, triple => _.isEqual(triple.subject, this.url)),
				mapping: {
					columns: ['predicate', 'object'],

					// Creates data object instance from row
					create (row) {
						return new RdfTriple.create(
							url,
							row.predicate,
							{
								type: Utils.isUrl(row.object) ? "url" : "literal",
								value: row.object
							}
						) 
					},

					// Creates row instance from data object 
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object,
							objectDatatype: data.objectDatatype
						}
					},

					// Updates existing data instance with data from row
					update (data, updatedRow) {
						data.subject = updatedRow.subject
						data.predicate = updatedRow.predicate
						data.object = updatedRow.object
						data.objectDatatype = updatedRow.objectDatatype
						return data
					}
				}
			},

			urlAsObject: {
				triples: _.filter(triples, triple => _.isEqual(triple.object, this.url)),
				mapping: {
					columns: ['subject', 'predicate'],

					// Creates data object instance from row
					create (row) {
						return new RdfTriple.create(
								row.subject,
								row.predicate,
								{
									type: "url",
									value: url
								}
						)
					},

					// Creates row instance from data object 
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object,
							objectDatatype: data.objectDatatype
						}
					},

					// Updates existing data instance with data from row
					update (data, updatedRow) {
						data.subject = updatedRow.subject
						data.predicate = updatedRow.predicate
						data.object = updatedRow.object
						data.objectDatatype = updatedRow.objectDatatype
						return data
					}
				}
			},

			blankNodes: {}, // TODO
		}
	},
	methods: {
		toggleEditableMode() {
			this.isEditableMode = !this.isEditableMode 
		},
		postPatchRequest() {
			let valid = true
			for (var i = 0; i < this.$children.length; i++) {
				let grid = this.$children[i]
				for (var j = 0; j < grid.$children.length; j++) {
					let row = grid.$children[j]
					for (var k = 0; k < row.$children.length; k++) {
						let cell = row.$children[k]
						if (cell.cssClass === 'invalid') {
							valid = false
						}
					}
				}
			}

			if (!valid) {
				alert("There are invalid triples. Please fix them and submit again.")
			} else {
				var patchJson = Object()
				patchJson.resourceUrl = this.url

				patchJson.addedData = [].concat(
					this.$refs.dataGridSubject.addedData,
					_.map(this.$refs.dataGridSubject.updatedData, d => d.to),
					this.$refs.dataGridObject.addedData,
					_.map(this.$refs.dataGridObject.updatedData, d => d.to)
				)

				patchJson.deletedData = [].concat(
					this.$refs.dataGridSubject.deletedData,
					_.map(this.$refs.dataGridSubject.updatedData, d => d.from),
					this.$refs.dataGridObject.deletedData,
					_.map(this.$refs.dataGridObject.updatedData, d => d.from)
				)

				$.post("/patch_requests", JSON.stringify(patchJson), function(response) {
					//TODO: nicer way of notification
					alert(response)
				})
			}
		}
	}
}
</script>
