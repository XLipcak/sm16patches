<template>
	<input class="editable-mode form-control" v-if="editableMode" placeholder="{{ column }}" v-model="row[column]" />
	<template v-else>
		<a v-show="isUrl(row[column])" href="row[column]">{{ row[column] }}</a>
		<span v-show="!isUrl(row[column])">{{ row[column] }}</span>	
	</template>
</template>

<script>
export default {
	props: {
		row: Object,
		column: String,
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		}
	},
	methods: {
		isUrl(data) {
			return data.startsWith("http://") || data.startsWith("https://")
		}
	}
}
</script>