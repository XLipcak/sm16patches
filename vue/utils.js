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
		var matchCount = /https?:\/\/.*\..*\/.*/.exec(data)
		if (matchCount && matchCount.length === 1) {
			return true;
		} else {
			return false;
		}
	}
}