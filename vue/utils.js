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
	}

//	/**
//	 * Filter triples where given 'url' is as subject.
//	 */ 
//	filterWhereUrlAsSubject (url, json) {
//		var result = _.filter(json, function (predicates, subject) {
//
//			return _.isEqual(subject, this.url)
//		}, {url: url})
//
//		console.log(result)
//		return result
//	},
/*

SUBJECT =>
	{  
      "http://dbpedia.org/ontology/influencedBy":[ <= PREDICATE 
         {  
            "type":"uri",
            "value":"http://dbpedia.org/resource/Albert_Einstein" <= OBJECT.VALUE
         }
      ],
      "http://dbpedia.org/property/influences":[ <= PREDICATE 
         {  
            "type":"uri",
            "value":"http://dbpedia.org/resource/Albert_Einstein" <= OBJECT.VALUE
         }
      ]
   }

*/	

//	/**
//	 * Filter triples where given 'url' is as object.
//	 */ 
//	filterWhereUrlAsObject (url, json) {
//		var result = _.filter(json, function (predicates, subject) {
//			return _.isEqual(subject, this.url)
//		}, {url: url})
//
//		console.log(result)
//		return result
//	},
}