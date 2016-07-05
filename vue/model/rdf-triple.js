export default {
	/**
	 * Data structure describing RDF Triple object.
	 */
	create(subject, predicate, object) {
		return {
			subject: subject,
			predicate: predicate,
			object: object.value,
			objectDatatype: object.type
		}
	},

	/**
	 * Construct flat array of triples from JSON object of following structure:
	 *    subject: { predicate: { object: {type: <string>, value: <string>} }
	 * 
	 * @param Object jsonObject 
	 * @return Array
	 */
	arrayOfTriplesFromJson (jsonObject) {
		var _tripleConsturctor = this.create; // TODO: Clean up

		var triples = []
		_.each(jsonObject, function(subjectValue, subject) {
			_.each(subjectValue, function (predicateValue, predicate) {
				_.each(predicateValue, function (objectRaw) {
					triples.push(new this._tripleConsturctor(this.subject, this.predicate, objectRaw))
				}, {subject: this.subject, predicate: predicate, _tripleConsturctor: this._tripleConsturctor})
			}, {subject: subject, _tripleConsturctor: _tripleConsturctor})
		}); 

		return triples
	}
}