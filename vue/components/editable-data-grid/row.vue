<template>
<tr>
	<td v-for="column in columns">
		<input v-model="row[column]" placeholder="{{ column }}" />
	</td>
	<td><button @click="removeRow(uuid)">X</button></td>
<tr>
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
export default {
	props: {
		'columns': Array,
		'uuid': String,
		'row': Object
	},
	watch: {
		row: {
			handler: function (updatedRow) {
				console.log("Row update dispatched")
				this.$dispatch('updateRow', this.uuid, updatedRow)
			},
			deep: true
		}
	},
	methods: {
		removeRow (uuid) {
			this.$dispatch('removeRow', uuid)
		}
	}
}
</script>