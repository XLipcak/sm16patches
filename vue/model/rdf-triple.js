export default {
	/**
	 * Data structure describing RDF Triple object.
	 */
	create(subject, predicate, object) {
		this.subject = subject;
		this.predicate = predicate;
		this.object = object;
	},

	/**
	 * Construct flat array of triples from JSON object of following structure:
	 *    subject: { predicate: { object: {type: <string>, value: <string>} }
	 */
	createListFromJson (jsonObject) {
		var _tripleConsturctor = this.create; // TODO: Clean up

		var triples = {}
		_.each(jsonObject, function(subjectValue, subject) {
			_.each(subjectValue, function (predicateValue, predicate) {
				_.each(predicateValue, function (objectRaw) {
					triples[this.subject] = new this._tripleConsturctor(this.subject, this.predicate, objectRaw)
				}, {subject: this.subject, predicate: predicate, _tripleConsturctor: this._tripleConsturctor})
			}, {subject: subject, _tripleConsturctor: _tripleConsturctor})
		}); 

		return triples
	}
}