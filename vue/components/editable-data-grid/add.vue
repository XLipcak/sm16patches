<template>
<tr>
	<td></td>
	<td v-for="attribute in attributes">
		<input v-model="newEntry[attribute]" placeholder="{{ attribute }}" />
	</td>
</tr>
<tr>
	<td></td>
	<td>
		<button @click="addEntry()">Add</button>
	</td>
</tr>
</template>



<script>
export default {
	props: ['attributes'],
	data: function() {
		return { newEntry: this.getClearNewEntry() }
	},
	methods: {
		getClearNewEntry() {
			var newEntry = {}
			_.each(this.attributes, function (attribute) {
				this.newEntry[attribute] = ""
			}, {newEntry: newEntry})

			return newEntry
		},
		addEntry() {
			if (_.some(this.newEntry, function (value) { return !_.isEmpty(value.trim()) })) {
				this.$dispatch('addEntry', this.newEntry)
				this.newEntry = this.getClearNewEntry()
			}
		}
	}
}
</script>