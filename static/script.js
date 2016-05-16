var EditableText = Vue.extend({
	data: ['updatedPredicate', 'updatedData'],
	props: ['predicate', 'data'],
	// template: '<input value="{{ data }}">'
})

new Vue({
	el: '.container',
	data: {
		editMode: true
	},
	components: {
		'editable-text': EditableText
	},
	methods: {
		toggleEditMode: function () {
			this.editMode = !this.editMode;
		},
		generatePatch: function () {
			console.log(_.map(this.$children, function(child) { return child.predicate + " -> " + child.data }));
		}
	}
});

console.log('Vue loaded');
	