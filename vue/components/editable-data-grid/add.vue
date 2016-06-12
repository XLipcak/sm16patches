<template>
<tr>
	<td v-for="(column, value) in newRow"><input class="editable-mode form-control" v-model="value" placeholder="{{ column }}" /></td>
	<td><button class="btn btn-success glyphicon glyphicon-plus" @click="addRow()"></button></td>
</tr>
</template>



<script>
export default {
	props: {
		columns: Array
	},
	data() {
		return {
			newRow: this.emptyRow()
		}
	},
	methods: {
		emptyRow () {
			return _.mapObject(_.object(this.columns, []), function() { return "" })
		},
		addRow () {
			// TODO: validate new entry, eg.: if (_.some(this.newEntry, function (value) { return !_.isEmpty(value.trim()) })) { ...
			this.$dispatch('addRow', this.newRow)
			this.newRow = this.emptyRow()
		}
	}
}
</script>