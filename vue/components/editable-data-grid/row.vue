<template>
<tr v-if="template == 'default'">
	<td v-for="column in columns">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			:column="column"
		></editable-cell>
	</td>
	<td><button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button></td>
<tr>

<tr v-if="template == 'subject'">
	<td>
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="predicate"
		></editable-cell>
	</td>
	<td>
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="object"
		></editable-cell>
	</td>
	<td><button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button></td>
</tr>

<tr v-if="template == 'object'">
	<td class="first">
		is <editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="predicate"
		></editable-cell> of 
	</td>	
	<td class="second">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="subject"
		></editable-cell>
	</td>
	<td><button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button></td>
</tr>
</template>



<script>
import EditableCell from './editable-cell.vue'

export default {
	props: {
		columns: Array,
		uuid: String,
		row: Object,
		editableMode: {
			type: Boolean,
			default: true,
			required: false
		},
		template: {
			type: String,
			default: 'default',
			required: false
		}
	},
	components: {
		'editable-cell': EditableCell 
	},
	watch: {
		row: {
			handler: function (updatedRow) {
				console.log("Row update dispatched")
				this.$dispatch('updateRow', this.uuid, updatedRow)
			},
			deep: true
		}
	},
	methods: {
		removeRow (uuid) {
			this.$dispatch('removeRow', uuid)
		}
	}
}
</script>