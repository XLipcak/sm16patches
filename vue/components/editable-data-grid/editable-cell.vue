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
		parseLiteral (value) {
			let literalRegex = new RegExp(["(\".*\")(\\^\\^xsd:(?:anyURI|boolean|date|dateTime|double|float|gDay|gMonth|",
					"gMonthDay|gYear|gYearMonth|integer|negativeInteger|nonNegativeInteger|nonPositiveInteger|positiveInteger|string|time))?"].join(''))
			let match = value.match(literalRegex)
			if (match) {
				if (match[2]) {
					console.log("WITH datatype")
				} else {
					console.log("WITHOUT datatype")
				}
			} else {
				console.log("url")
			}
			console.log(match)
			return match
		},
		autocomplete () {
			if (this.column !== "predicate") return null;

			var searchString = $("#" + this.uuid + "input").val()
			searchString = searchString.split("/").slice(-1)[0]

			if (searchString === "") {
				return null;
			}

			let apiUrl = "http://lov.okfn.org/dataset/lov/api/v2/term/search?q=" + searchString + "&type=property&page_size=100"
			let inputId = this.uuid + 'input'
			let autocompleteSource = []

			let xhr = new XMLHttpRequest()
			xhr.onreadystatechange = function() {
				if (xhr.readyState == XMLHttpRequest.DONE) {
					let response = JSON.parse(xhr.response)
					response.results.forEach( function(entry) {
						autocompleteSource.push(entry.uri[0])
					})
					$("#"+inputId).autocomplete({
						source: autocompleteSource,
					})
				}
			}

			xhr.open('GET', apiUrl)
			xhr.send()
		},
		onPropertyGetSuccess(response) {
			console.log(reponse)
		}
	},
	computed: {
		value: function() {
			return this.row[this.column]
		},
		valueIsUrl: function() {
			return Utils.isUrl(this.value)
		},
		valueIsLiteral: function() {
			return this.parseLiteral(this.value)
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