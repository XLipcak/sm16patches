<template>
<tr>
	<td>{{ key }}</td>
	<td v-for="attribute in data">
		<input v-model="attribute" value="{{ attribute }}" />
	</td>
	<td>
		<button @click="removeEntry(key)">X</button>
	</td>
<tr>
</template>



<script>
export default {
	props: ['key', 'data'],
	watch: {
		data: {
			handler: function (val) {
				console.log('Something chagned to ' + JSON.stringify(val))
			},
			deep: true
		}
	},
	methods: {
		removeEntry (uuid) {
			this.$dispatch('removeEntry', uuid)
		}
	}
}
</script>