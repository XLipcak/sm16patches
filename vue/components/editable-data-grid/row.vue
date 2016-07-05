<template>
<tr v-if="template == 'default'">
	<td v-for="column in columns">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			:column="column"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td><button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button></td>
<tr>

<tr v-if="template == 'subject'">
	<td>{{ row.subject }}</td>
	<td calss="first">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="predicate"
			:datatype="'uri'"
			:uuid="uuid + 'predicate'"
		></editable-cell>
	</td>
	<td calss="second">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="object"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td><button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button></td>
</tr>

<tr v-if="template == 'object'">
	<td class="first">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="subject"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td class="second">
		<editable-cell
			:editable-mode="editableMode"
			:row="row"
			column="predicate"
			:datatype="'uri'"
			:uuid="uuid + 'predicate'"
		></editable-cell>
	</td>	
	<td>{{ row.object }}</td>
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