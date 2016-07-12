export default {
	/**
	 * UUID v4
	 */
	uuid () {
		function s4() {
			return Math.floor((1 + Math.random()) * 0x10000)
				.toString(16)
				.substring(1)
		}
		return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
			s4() + '-' + s4() + s4() + s4()
	},

	/**
	 * Transforms plain Array to Object, where key is UUID.
	 */
	createUuidList (data) {
		var uuidList = {};
		_.each(data, function (entry) {
				this.uuidList[this.uuid()] = entry
		}, {uuid: this.uuid, uuidList: uuidList})

		return uuidList
	},

	isUrl(data) {
		// this regex does not include non allowed characters yet
		var matchCount = /^https?:\/\/.*\..*\/.*/.exec(data)
		if (matchCount && matchCount.length === 1) {
			return true;
		} else {
			return false;
		}
	},

	/**
	 * Performs autocomplete of RDF URL's
	 */
	autocomplete (column, uuid) {
		if (column !== "predicate") return null;

		var searchString = $("#" + uuid + "input").val()
		searchString = searchString.split("/").slice(-1)[0]

		if (searchString === "") {
			return null;
		}

		let apiUrl = "http://lov.okfn.org/dataset/lov/api/v2/term/search?q=" + searchString + "&type=property&page_size=100"
		let inputId = uuid + 'input'
		let autocompleteSource = []

		let xhr = new XMLHttpRequest()
		xhr.onreadystatechange = function() {
			if (xhr.readyState == XMLHttpRequest.DONE) {
				let response = JSON.parse(xhr.response)
				response.results.forEach( function(entry) {
					autocompleteSource.push(entry.uri[0])
				})
				$("#"+inputId).autocomplete({
					source: autocompleteSource,
				})
			}
		}

		xhr.open('GET', apiUrl)
		xhr.send()
	}
}