module.exports = {
	entry: './vue/app.js',
	output: {
		path: __dirname + "/static/js",
		filename: "vue-app.build.js"
	},
	module: {
		loaders: [
			{
				test: /\.js$/,
				loader: 'babel',
				exclude: /node_modules/
			},
			{
				test: /\.vue$/,
				loader: 'vue'
			}
		]
	},
	vue: {
		loaders: {
			js: 'babel'
		}
	}
}