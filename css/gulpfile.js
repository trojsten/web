const gulp = require('gulp');
const cache = require('gulp-cached');
const less = require('gulp-less');
const rename = require('gulp-rename');
const cleanCSS = require('gulp-clean-css');

const distDest = '../trojsten/static/css/';

gulp.task('less', function() {
  return gulp.src('src/{ksp,fks,kms,trojsten}.less')
    .pipe(cache('less'))
    .pipe(less())
    .pipe(cleanCSS())
    .pipe(rename(function (path) {
      path.dirname += '/' + path.basename;
      path.extname = '.min.css';
    }))
    .pipe(gulp.dest(distDest));
});

gulp.task('watch', function(){
  gulp.watch('src/*.less', ['less']);
});

gulp.task('default', ['watch']);
