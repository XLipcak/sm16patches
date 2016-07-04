<template xmlns:v-on="http://www.w3.org/1999/xhtml">
	<h1>RDF</h1>
	<h2>About: <a href= "{{ url }}"> {{url}} </a> </h2>
	<div class="form-group">
		<label for="searchText">Filter:</label>
		<input type="hidden" name="url" value="{{url}}" />
		<input v-model="searchString" id="searchText" name="searchText" placeholder="Search..." value="{{searchText}}" class="form-control" type="text" />
	</div>

	<h3>Triples where <a href= "{{ url }}"> {{ url }} </a> is the subject:</h3>
	<editable-data-grid
		v-ref:data-grid-subject
		row-template="subject"
		:data="urlAsSubject.triples"
		:mapping="urlAsSubject.mapping"
		:filter-string="searchString"
		:editable-mode="isEditableMode"
	></editable-data-grid>

	<h3>Triples where <a href= "{{url}}"> {{ url }} </a> is the object:</h3>
	<editable-data-grid
		v-ref:data-grid-object
		row-template="object"
		:data="urlAsObject.triples"
		:mapping="urlAsObject.mapping"
		:filter-string="searchString"
		:editable-mode="isEditableMode"
	></editable-data-grid>

	<h3>Blank nodes</h3>
	<em>To be done.</em>

	<div class="footer navbar-fixed-bottom">
		<div class="panel panel-default panel-bottom">
			<div class="panel-body">
				<button type="button" class="btn btn-default" @click="toggleEditableMode">Editable mode: {{ isEditableMode }}</button>
				<button type="button" class="btn btn-default" data-toggle="modal" data-target="#patchModal">
					View changes
				</button>
				<button id="submitPatch" type="button" class="btn btn-primary" v-on:click="postPatchRequest">Submit Patch Request</button>
			</div>
		</div>	
	</div>

	<!-- Recorded chagnes Modal -->
	<div class="modal fade" id="patchModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel">Recorded changes</h4>
				</div>
				<div class="modal-body">
					<h4>Triples where <a href= "{{ url }}"> {{ url }} </a> is the subject:</h4>
					<h5>Added</h5>
					<pre>{{ $refs.dataGridSubject.addedData | json }}</pre>
					<h5>Updated</h5>
					<pre>{{ $refs.dataGridSubject.updatedData | json }}</pre>
					<h5>Deleted</h5>
					<pre>{{ $refs.dataGridSubject.deletedData | json }}</pre>

					<h4>Triples where <a href= "{{url}}"> {{ url }} </a> is the object:</h4>
					<h5>Added</h5>
					<pre>{{ $refs.dataGridObject.addedData | json }}</pre>
					<h5>Updated</h5>
					<pre>{{ $refs.dataGridObject.updatedData | json }}</pre>
					<h5>Deleted</h5>
					<pre>{{ $refs.dataGridObject.deletedData | json }}</pre>				</div>
			</div>
		</div>
	</div>				


<!-- ORIGINAL PYTHON TEMPLATE -->

<!--
	<h2>About: <a href= "{{url}}"> {{url}} </a> </h2>
	<form action="{{reverse_url('resource')}}" method="get">
		<div class="form-group">
			<label for="searchText">Filter:</label>
			<input type="hidden" name="url" value="{{url}}" />
			<input id="searchText" name="searchText" placeholder="Search..." value="{{searchText}}" class="form-control" type="text" />
			<button type="submit" class="btn btn-default">Submit</button>
		</div>
	</form>

	<h3>Triples where <a href= "{{url}}"> {{url}} </a> is the subject:</h3>
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

	<h3>Triples where <a href= "{{url}}"> {{url}} </a> is the object:</h3>
	<table class="table">
		<tbody>
			{% for subject, predicate, object in rdfGraph.triples( (None, None, URIRef(url)) ) %}
				<tr>
					<td class="first">is <a href="{{ predicate }}">{{ predicate }}</a> of</td>
					{% if isinstance(object, URIRef) %}
						<td class="second">
							<p class="break">
								<a href="{{subject}}">{{ subject }}</a>
							</p>
						</td>
					{% else %}
						<td class="second">
							<p class="break">
								{{ subject }}
							</p>
						</td>
					{% end %}
				</tr>
			{% end %}						
		</tbody>
	</table>

	<h3>Blank nodes</h3>
	<table class="table">
		<tbody>
			{% for subject, predicate, object in rdfGraph.triples( (None, None, None) ) %}
				{% if isinstance(subject, BNode) %}
				<tr>
					<td>{{ subject }}</td>
					<td>{{ predicate }}</td>
					<td>{{ object }}</td>
				</tr>
				{% end %}
			{% end %}						
		</tbody>
	</table>
-->	
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
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object,
							objectDatatype: data.objectDatatype,
						}
					},
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
					columns: ['predicate', 'subject'],
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
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object,
							objectDatatype: data.objectDatatype,
						}
					},
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
