## Setup
Install NodeJS dependencies
```
npm install
```
Compile JavaScripts using webpack
```
webpack
```

## Run server
[Tornado](http://www.tornadoweb.org/ "Tornado") web server used. Python 2.7 needed (does not work with 3.4), server will run on [http://localhost:8888/](http://localhost:8888/)
```
python server.py
```

## Development
Run _webpack_ in watch mode recompile JavaScript on file change automatically
```
webpack --watch
```