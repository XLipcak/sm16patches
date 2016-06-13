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
		return data.startsWith("http://") || data.startsWith("https://")
	}
}