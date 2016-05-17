$(document).ready(function() {
	var data = [];
	var editMode = false;
	
	function findNonRecursive(element, selector, found) {
		var newFound = found;
		$(element).children().each(function (idx, child) {
			if ($(child).is(selector)) {
				newFound.push(child);
			} else {
				findNonRecursive(child, selector, newFound);
			}
		});
		
		return newFound;
	}

	function parseGroup(group) {
		var editElement = $('.rdf-element:first', group);
		
		return {
			name: editElement.attr('data-name'),
			value: editElement.text(),
			children: _.map(findNonRecursive(group, '.rdf-group', []), parseGroup)
		};
	};
	
	$('.button.rdf-toggle-edit-mode').click(function() {
		editMode = !editMode;
		$('.rdf-element').each(function (idx, el) {
			$(el).attr('contenteditable', editMode);
			if (editMode) {
				$(el).addClass('rdf-element-in-edit');
			} else {
				$(el).removeClass('rdf-element-in-edit');
			}
		});
	});
	
	$('.button.rdf-generate-patch').click(function() {
		console.log(
			JSON.stringify(
				_.map(findNonRecursive($('.container'), '.rdf-group', []), parseGroup),
				null,
				2
			)
		)
	});	
});
