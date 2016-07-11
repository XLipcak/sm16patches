<template xmlns:v-on="http://www.w3.org/1999/xhtml">
<td v-for="value in rangeEmptyColumnsLeft"></td>
<template v-if="isPredicateFirst()">
	<td>
		<input
			class="editable-mode form-control"
			v-model="predicate"
			placeholder="Predicate (type to get suggestions)"
			:id="'suggest1input'"
			v-on:keyup="autocomplete(columns[0], 'suggest1')"
		/>
	</td>
	<td>
		<input
			class="editable-mode form-control"
			v-model="object"
			placeholder="Object"
			:id="this.uuid + 'input'"
			v-on:keyup="autocomplete(columns[1], uuid)"
		/>
	</td>
</template>
<template v-else>
	<td>
		<input
			class="editable-mode form-control"
			v-model="subject"
			placeholder="Subject"
			:id="this.uuid + 'input'"
			v-on:keyup="autocomplete(columns[0], uuid)"
		/>
	</td>
	<td>
		<input
			class="editable-mode form-control"
			v-model="predicate"
			placeholder="Predicate (type to get suggestions)"
			:id="'suggest2input'"
			v-on:keyup="autocomplete(columns[1], 'suggest2')"
		/>
	</td>
</template>
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
		},
		isPredicateFirst() {
			if (this.columns[0] === 'predicate') {
				return true
			}
			return false
		}
	},
}
</script>