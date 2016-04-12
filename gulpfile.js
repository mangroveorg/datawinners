"use strict";

var gulp = require("gulp");
var browserify = require('browserify');
var reactify = require('reactify');
var source = require('vinyl-source-stream');
var concat = require('gulp-concat');
var babelify = require('babelify');
var exorcist = require('exorcist');

var config = {
	    paths: {
	      dist : './datawinners/media/javascript/questionnaire_builder/dist',
				dist_css: './datawinners/media/css/questionnaire_builder/dist',
	      main_js : './datawinners/media/javascript/questionnaire_builder/src/main.js',
	      js : './datawinners/media/javascript/questionnaire_builder/src/**/*.js',
	      css: [
	            'node_modules/toastr/build/toastr.min.css',
	            './datawinners/media/css/questionnaire_builder/**/*.css'

	      	]

	    }
	};

gulp.task('js', function() {
	browserify({
		entries: [config.paths.main_js],
		debug:true
	})
		.transform([babelify,reactify])
		.bundle()
		.pipe(exorcist(config.paths.dist+'/bundle.js.map'))
		.on('error', console.error.bind(console))
		.pipe(source('bundle.js'))
		.pipe(gulp.dest(config.paths.dist))
});

gulp.task('watch', function(){
	gulp.watch(config.paths.js, ['js']);
})

gulp.task('css', function() {
	gulp.src(config.paths.css)
		.pipe(concat('bundle.css'))
		.pipe(gulp.dest(config.paths.dist_css));
});

gulp.task("default",["js","css", "watch"])
