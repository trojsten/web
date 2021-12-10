'use strict';

angular.module('zerg.controllers', [])
    .controller('SeriesCtrl', ['$rootScope', '$scope', 'Levels',
        function ($rootScope, $scope, Levels) {
        	Levels({}).get(function (data) {
        	    $rootScope.series = data.series;
        	}, function (data) {
        	    // Error
        	});
            $scope.staticUrlPrefix = STATIC_URL_PREFIX;
        }])
    .controller('LevelsCtrl', ['$rootScope', '$scope', '$routeParams', 'Levels',
        function ($rootScope, $scope, $routeParams, Levels) {

        	Levels({}).get(function (data) {
        	    $rootScope.series = data.series;
        	}, function (data) {
        	    // Error
        	});

            $rootScope.seriesName = $rootScope.series[$routeParams.seriesId].name;
            $scope.seriesName = $rootScope.series[$routeParams.seriesId].name;

            $scope.levels = $rootScope.series[$routeParams.seriesId].levels;
            $scope.staticUrlPrefix = STATIC_URL_PREFIX;
        }])
    .controller('GameCtrl', ['$scope', '$routeParams', '$location', '$timeout',
                             'Levels', 'Solutions', 'Submits', 'ngDialog',
        function ($scope, $routeParams, $location, $timeout, Levels, Solutions, Submits, ngDialog) {

            var getCookie = function (name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            };

            $scope.$on('$destroy', function () {
                if ($scope.game) {
                    $scope.game.destroy();
                }
            });

            $scope.aceLoaded = function (e) {
                $scope.editor = e;
            };

            $scope.aceChanged = function (e) {
                $scope.programRaw = e[1].getValue()
                var program = new Program($scope.programRaw);
                $scope.program = program;
                e[1].getSession().clearAnnotations();
                var newAnnotations = [];
                if (program.errors.length != 0) {
                    for (var i = 0; i < program.errors.length; i++) {
                        newAnnotations.push({
                            'row': program.errors[i].original_line,
                            'text': program.errors[i].description,
                            'type': 'error'
                        });
                    }
                    e[1].getSession().setAnnotations(newAnnotations);
                }
                $scope.memory_usage = 0;

                for (var i in program.subroutines) {
                    $scope.memory_usage += program.subroutines[i].instructions.length;
                }
            };

            $scope.memory_usage = 0;

            $scope.resetGame = function () {

                if ($scope.running) {
                    return;
                }

                $scope.level.logic_map = jQuery.extend(true, {}, $scope.level.logic_map_bup);

                $scope.levelView.redraw_level();
                $scope.bot.moveTo($scope.level.startX, $scope.level.startY, $scope.level.startFacing);

                $scope.remaining_battery = $scope.level.battery_limit;

                $scope.editor.setReadOnly(false);
                $scope.editor.setHighlightActiveLine(true);
                $scope.editor.getSession().removeMarker($scope.execution_marker);

                $scope.warping = false;
                ANIMATION_DURATION = ANIMATION_DURATION_NORMAL;

            };

            $scope.exitGame = function () {
                $location.path("series");
            };

            $scope.clearEditor = function () {
                if ($scope.running) {
                    return;
                }
                $scope.editor.setValue('');
                $scope.editor.getSession().setAnnotations([]);
            };

            $scope.timewarp = function () {
                if (!$scope.running) {
                    return;
                }
                $scope.warping = !$scope.warping;
                switch (ANIMATION_DURATION) {
                    case ANIMATION_DURATION_NORMAL:
                        ANIMATION_DURATION = ANIMATION_DURATION_SHORT;
                        break;
                    case ANIMATION_DURATION_SHORT:
                        ANIMATION_DURATION = ANIMATION_DURATION_VERYSHORT;
                        break;
                    case ANIMATION_DURATION_VERYSHORT:
                        ANIMATION_DURATION = ANIMATION_DURATION_NORMAL;
                        break;
                }

                $scope.warping = ANIMATION_DURATION != ANIMATION_DURATION_NORMAL;
                $scope.warping_fast = ANIMATION_DURATION == ANIMATION_DURATION_VERYSHORT;
            };

            $scope.showSolution = function () {
                $scope.solutionBeingDownloaded = true;
                Solutions({"X-CSRFToken": getCookie('csrftoken')}).get({levelId: $routeParams.levelId})
                    .$promise.then(function (value) {
                        if ($scope.editor.getValue() != '') {
                            if (confirm('Vzorové riešenie prepíše váš program. Pokačovať?')) {
                                $scope.editor.setValue(value.solution);
                                $scope.solutionBeingDownloaded = false;
                            } else {
                                $scope.solutionBeingDownloaded = false;
                            }
                        } else {
                            $scope.editor.setValue(value.solution);
                            $scope.solutionBeingDownloaded = false;
                            $scope.aceChanged([null, $scope.editor]);
                        }
                    }, function (value) {
                        alert('Nemáš právo vidieť riešenie. Grrrr!');
                        $scope.solutionBeingDownloaded = false;
                    });
            }

			$scope.runAllowed = false;
			$scope.level = Levels({}).get({levelId: $routeParams.levelId});
			$scope.level.$promise.then(function(value) {

				$scope.loaded = true;

				ngDialog.open({
				    template: STATIC_URL_PREFIX + 'partials/levelDescriptionDialog.html',
				    className: 'ngdialog-theme-default',
				    scope: $scope
				});

				$scope.remaining_battery = $scope.level.battery_limit;

				var setLevelDivSize = function() {
					var level_area = $(".level_area");
					var level = $("#level");
                    var level_overlay = $("#level_overlay");

					level.width(level_area.width()-20);
					level.height(level_area.height());

                    level_overlay.width(level_area.width()-20);
                    level_overlay.height(level_area.height());
				}

				setLevelDivSize();
				$(window).resize(setLevelDivSize);

				$scope.game = new Phaser.Game("100%", "100%", Phaser.CANVAS, 'level', null, true);
    			$scope.game.state.add('Boot', ProjectZerg.Boot);
    			$scope.game.state.add('Preloader', ProjectZerg.Preloader);
    			$scope.game.state.add('Game', ProjectZerg.Game)
    			$scope.game.state.start('Boot');
    			$scope.game.level = $scope.level;
    			$scope.game.setZergCallbacks = function(levelView, bot) {
    				$scope.levelView = levelView;
    				$scope.bot = bot;
    				$scope.runAllowed = true;
    			}

    			$scope.level.logic_map_bup = jQuery.extend(true, {}, $scope.level.logic_map);

			}, function(value) {
				$location.path("series")
			});

			$scope.runClick = function() {

				if ($scope.runAllowed === false) {
					return;
				}

				if ($scope.running === true) {
					$scope.pleaseStop = true;
					return;
				}

				if ($scope.program === undefined || $scope.program.subroutines.main.instructions.length == 0) {
					alert('Nemôžem spustiť prázdny program!');
					return;
				} else if ($scope.program.errors.length != 0) {
					alert('Program obsahuje chyby!');
					return;
				} else if ($scope.memory_usage > $scope.level.memory_limit) {
					alert('Program sa nezmestí do pamäte!');
					return;
				}

				$scope.resetGame();
				$scope.pleaseStop = false;
				$scope.editor.setReadOnly(true);
				$scope.editor.setHighlightActiveLine(false);

				var interpreter = new ZergInterpreter($scope.program, $scope.level, function(x, y) {
					$scope.bot.walkTo(x, y);
				}, function() {
					$scope.bot.rotateRight();
				}, function() {
					$scope.bot.rotateLeft();
				}, function() {
					$scope.levelView.redraw_level();
				}, function(line) {

					var Range = ace.require("ace/range").Range;
					$scope.editor.getSession().removeMarker($scope.execution_marker);
					$scope.execution_marker = $scope.editor.getSession().addMarker(new Range(line, 0, line+1, 0), "ace_executing", "background");

				}, function(remaining_battery) {
					$scope.remaining_battery = remaining_battery;
                    // https://stackoverflow.com/questions/29817111/when-is-it-safe-to-use-scope-apply
                    $timeout( function(){
                        $scope.$apply();
                    }, 0);
				});

				var execute = function() {
					$scope.running = true;
					var sim_status;
					if((sim_status = interpreter.programStep()) === interpreter.SIM_OK && $scope.pleaseStop !== true) {
						setTimeout(execute, ANIMATION_DURATION * 2);
					} else {
						$scope.running = false;
						var postmortum = function() {
							switch (sim_status) {
								case interpreter.SIM_LEVEL_PASSED:

                                    $scope.submitFailed = false;
                                    $scope.submitSuccess = false;
                                    $scope.submitInProgress = false;
                                    $scope.submitUnrated = false;

                                    ngDialog.open({
                                        template: STATIC_URL_PREFIX + 'partials/levelSubmit.html',
                                        className: 'ngdialog-theme-default',
                                        scope: $scope
                                    });

                                    if (!$scope.level.solved) {

                                        // Solution submit
                                        $scope.submitInProgress = true;
                                        Levels({"X-CSRFToken": getCookie('csrftoken')}).submitLevel({
                                            levelId: $routeParams.levelId
                                        }, {"programRaw": $scope.programRaw}, function(data) {
                                            $scope.submitInProgress = false;
                                            if (data.type == "UNRATED") {
                                                $scope.submitUnrated = true;
                                                $scope.level.solved = true;
                                                return
                                            }

                                            if (data.type == "SOLVED") {
                                                $scope.submitSuccess = true;
                                                $scope.level.solved = true;
                                                return
                                            }

                                            if (data.type != "TESTED") {
                                                $scope.submitFailed = true;
                                                return
                                            }

                                            if (data.result == 1) {
                                                $scope.submitSuccess = true;
                                                $scope.level.solved = true;
                                            } else {
                                                $scope.submitFailed = true;
                                            }

                                        }, function() {
                                            $scope.submitInProgress = false;
                                            $scope.submitFailed = true;
                                        });
                                    }

									break;
								case interpreter.SIM_DEAD_JETTORCH:
									alert('Zabil ťa oheň!');
									break;
								case interpreter.SIM_NO_BATTERY:
									alert('Došla batéria!');
									break;
							}
							$scope.editor.setReadOnly(false);
							$scope.editor.setHighlightActiveLine(true);
							$scope.editor.getSession().removeMarker($scope.execution_marker);
							$scope.pleaseStop = false;
							$scope.running = false;
                            $timeout( function(){
                                $scope.$apply();
                            }, 0);
						}
						setTimeout(postmortum, ANIMATION_DURATION * 2);
					}
				}

				execute();

			};

            $scope.showHintDialog = function() {
                ngDialog.open({
                    template: STATIC_URL_PREFIX + 'partials/levelHintDialog.html',
                    className: 'ngdialog-theme-default',
                    scope: $scope
                });
            };
        }]);
