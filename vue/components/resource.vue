<template>
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
				<button type="button" class="btn btn-primary" v-on:click="postPatchRequest">Submit Patch Request</button>
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
		url: String
	},
	data () {
		var jsonObject = JSON.parse(this.jsonData)
		var triples = RdfTriple.arrayOfTriplesFromJson(jsonObject)

		return {
			isEditableMode: true,
			searchString: "",
			urlAsSubject: {
				triples: _.filter(triples, triple => _.isEqual(triple.subject, this.url)),
				mapping: {
					columns: ['predicate', 'object'],
					create (row) {
						return new RdfTriple.create("", row.predicate, { type: "url", value: row.object }) 
					},
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object.value, 
						}
					},
					update (data, updatedRow) {
						data.subject = updatedRow.subject
						data.predicate = updatedRow.predicate
						data.object.value = updatedRow.object
						return data
					}
				}
			},

			urlAsObject: {
				triples: _.filter(triples, triple => _.isEqual(triple.object.value, this.url)),
				mapping: {
					columns: ['predicate', 'subject'],
					create (row) {
						return new RdfTriple.create(row.subject, row.predicate, { type: "text", value: "" }) 
					},
					read (data) {
						return {
							subject: data.subject,
							predicate: data.predicate, 
							object: data.object.value, 
						}
					},
					update (data, updatedRow) {
						data.subject = updatedRow.subject
						data.predicate = updatedRow.predicate
						data.object.value = updatedRow.object
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
			var patchJson = Object();
			patchJson.addedData = this.$refs.dataGridSubject.addedData.concat(this.$refs.dataGridObject.addedData);
			patchJson.deletedData = this.$refs.dataGridSubject.deletedData.concat(this.$refs.dataGridObject.deletedData);
			patchJson.updatedData = this.$refs.dataGridSubject.updatedData.concat(this.$refs.dataGridObject.updatedData);

			$.post("/patch_requests", JSON.stringify(patchJson));
		}
	}
}
</script>
