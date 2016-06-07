<template>
<!--
	<pre>{{ url }}</pre>
	<pre>{{ jsonData }}</pre>
	<pre>{{ urlAsObject | json }}</pre>
-->

	<h1>RDF</h1>
	<h2>About: <a href= "{{ url }}"> {{url}} </a> </h2>
	<div class="form-group">
		<label for="searchText">Filter:</label>
		<input type="hidden" name="url" value="{{url}}" />
		<input id="searchText" name="searchText" placeholder="Search..." value="{{searchText}}" class="form-control" type="text" />
		<button type="submit" class="btn btn-default">Submit</button>
	</div>

	<h3>Triples where <a href= "{{ url }}"> {{ url }} </a> is the subject:</h3>
	<editable-data-grid	:data="urlAsSubject.triples" :mapping="urlAsSubject.mapping"></editable-data-grid>

<!--
	<h3>Triples where <a href= "{{url}}"> {{ url }} </a> is the object:</h3>
	<editable-data-grid url="{{ url }}" :data="urlAsObject"></editable-data-grid>
-->
	<h3>Blank nodes</h3>
	<em>To be done.</em>

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
		var triples = RdfTriple.createListFromJson(jsonObject)

		return {
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

			urlAsObject: _.filter(triples, triple => _.isEqual(triple.object.value, this.url)),

			blankNodes: {}, // TODO
		}
	}
}
</script>
