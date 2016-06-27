<template>
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
		valueIsUrl: function() {
			return Utils.isUrl(this.row[this.column])
		},
		valueIsValid: function() {
			if (this.valueIsUrl) {
				return true
			}
			return false
		},
	},
}
</script>