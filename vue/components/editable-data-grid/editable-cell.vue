<template xmlns:v-bind="http://www.w3.org/1999/xhtml" xmlns:v-on="http://www.w3.org/1999/xhtml">
	<input
			id="{{uuid + 'input'}}"
			type="text"
			v-bind:class="['editable-mode', 'form-control', valueIsValid ? 'valid' : 'invalid']"
			v-if="editableMode" placeholder="{{ column }}"
			v-model="row[column]"
			v-on:keyup="autocomplete"
	/>
	<template v-else>
		<a v-show="isUrl(row[column])" href="row[column]">{{ row[column] }}</a>
		<span v-show="!isUrl(row[column])">{{ row[column] }}</span>	
	</template>
</template>

<script>
import Utils from './../../utils.js'

export default {
	props: {
		row: Object,
		column: String,
		datatype: String,
		uuid: String,
		xhr: Function,
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		}
	},
	methods: {
		isUrl (data) {
			return Utils.isUrl(data)
		},
		autocomplete () {
			if (this.column !== "predicate") return null;
			try {
				this.xhr.abort()
			} catch (e) {
				console.log(e)
			} finally {
				var searchString = $("#" + this.uuid + "input").val()
				searchString = searchString.split("/").slice(-1)[0]
				let apiUrl = "http://lov.okfn.org/dataset/lov/api/v2/term/search?q=" + searchString + "&type=property&page_size=100"
				let inputId = this.uuid + 'input'
				let autocompleteSource = []

				let source = [
					"nutte",
					"hurensohn",
				]
				this.xhr = $.get(apiUrl).success( function(response) {
					response.results.forEach( function(entry) {
						console.log(entry.uri[0])
						autocompleteSource.push(entry.uri[0])
					})
					$("#"+inputId).autocomplete({
						source: autocompleteSource,
					})
				})

			}
		}
	},
	computed: {
		value: function() {
			return this.row[this.column]
		},
		valueIsUrl: function() {
			return Utils.isUrl(this.value)
		},
		valueIsValid: function() {
			if (this.datatype === 'uri') {
				return this.valueIsUrl
			} else if (this.datatype === 'literal') {
				return !this.valueIsUrl
			}
			return false
		},
	},
}
</script>