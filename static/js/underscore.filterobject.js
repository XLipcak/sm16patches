(function(root, factory) {

  if (typeof exports !== 'undefined') {
    var _ = require('underscore');
    if (typeof module !== 'undefined' && module.exports)
      module.exports = factory(_);
    exports = factory(_);
  } else {
    root._.mixin(factory(root._));
  }

}(this, function(_) {

  return {
	filterObject: function(obj, predicate, context) {
        return _.reduce(obj, function(memo, val, key) {
            if (predicate.call(context, val, key, memo)) memo[key] = val;
            return memo;
        }, {});
    }
  };

}));