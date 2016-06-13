<template>
	<input class="editable-mode form-control" v-if="editableMode" placeholder="{{ column }}" v-model="row[column]" />
	<template v-else>
		<a v-show="Utils.isUrl(row[column])" href="row[column]">{{ row[column] }}</a>
		<span v-show="!Utils.isUrl(row[column])">{{ row[column] }}</span>	
	</template>
</template>

<script>
import Utils from './../../utils.js'

export default {
	props: {
		row: Object,
		column: String,
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		}
	}
}
</script>