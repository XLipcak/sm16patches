<template>
<!-- Defualt template: renders all fields as editable. -->
<tr v-if="template == 'default'">
	<td v-for="column in columns">
		<editable-cell
			:editable-mode="editableMode"
			:column="column"
			:value="row[column]"
			:original-value="originalRow[column]"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td>
		<button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button>
	</td>
<tr>

<!-- Renders 'subject' field as non-editable and 'predicate' and 'object' fields as editable. All other fields are skipped. -->
<tr v-if="template == 'subject'">
	<td>
		<span class="input-padding">{{ row.subject }}</span>
	</td>
	<td>
		<editable-cell
			:editable-mode="editableMode"
			column="predicate"
			:value="row['predicate']"
			:original-value="originalRow['predicate']"
			:datatype="'uri'"
			:uuid="uuid + 'predicate'"
		></editable-cell>
	</td>
	<td>
		<editable-cell
			:editable-mode="editableMode"
			column="object"
			:value="row['object']"
			:original-value="originalRow['object']"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td>
		<button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button>
	</td>
</tr>

<!-- Renders 'object' field as non-editable and 'subject' and 'predicate' fields as editable. All other fields are skipped. -->
<tr v-if="template == 'object'">
	<td>
		<editable-cell
			:editable-mode="editableMode"
			column="subject"
			:value="row['subject']"
			:original-value="originalRow['subject']"
			:datatype="row.objectDatatype"
		></editable-cell>
	</td>
	<td>
		<editable-cell
			:editable-mode="editableMode"
			column="predicate"
			:value="row['predicate']"
			:original-value="originalRow['predicate']"
			:datatype="'uri'"
			:uuid="uuid + 'predicate'"
		></editable-cell>
	</td>	
	<td>
		<span class="input-padding">{{ row.object }}</span>
	</td>
	<td>
		<button class="btn btn-danger glyphicon glyphicon-remove" v-show="editableMode" @click="removeRow(uuid)"></button>
	</td>
</tr>
</template>



<script>
import EditableCell from './editable-cell.vue'

export default {
	props: {
		columns: Array,
		uuid: String,
		row: Object,
		originalRow: Object,
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
	events: {
		updatedValue(column, updatedValue) {
			this.row[column] = updatedValue // Isn't this little hacky?
			this.$dispatch('updateRow', this.uuid, this.row)
		}
	},
	methods: {
		removeRow (uuid) {
			this.$dispatch('removeRow', uuid)
		}
	}
}
</script>