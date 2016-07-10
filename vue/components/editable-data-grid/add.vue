<template>
<td v-for="value in rangeEmptyColumnsLeft"></td>
<td v-for="(column, value) in newRow">
	<input
		class="editable-mode form-control"
		v-model="value"
		placeholder="{{ column }}"
		:id="this.uuid + 'input'"
		v-on:keyup="autocomplete(column, uuid)"
	/>
</td>
<td v-for="value in rangeEmptyColumnsRight"></td>
<td>
	<button class="btn btn-success glyphicon glyphicon-plus" @click="addRow()"></button>
</td>
</template>



<script>
import Utils from './../../utils.js'

export default {
	props: {
		columns: Array,
		emptyColumnsLeft: Number,
		emptyColumnsRight: Number,
	},
	data() {
		return {
			newRow: this.emptyRow(),
			rangeEmptyColumnsLeft: _.range(this.emptyColumnsLeft),
			rangeEmptyColumnsRight: _.range(this.emptyColumnsRight),
			uuid: Utils.uuid()
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
		},
		autocomplete (column, uuid) {
			return Utils.autocomplete(column, uuid)
		}
	}
}
</script>