<template xmlns:v-bind="http://www.w3.org/1999/xhtml">
	<input type="text" v-bind:class="['editable-mode', 'form-control', valueIsValid ? 'valid' : 'invalid']" v-if="editableMode" placeholder="{{ column }}" v-model="row[column]" />
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
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		}
	},
	methods: {
		isUrl (data) {
			return Utils.isUrl(data)
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