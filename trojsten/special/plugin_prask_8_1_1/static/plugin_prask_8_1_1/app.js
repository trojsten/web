'use strict';

angular.module('zerg', [
    'ngRoute',
    'ngResource',
    'ngDialog',
    'ui.ace',
    'zerg.controllers',
    'zerg.services'
])
    
    .config(['$routeProvider', '$sceDelegateProvider', function ($routeProvider, $sceDelegateProvider) {

        $sceDelegateProvider.resourceUrlWhitelist([
            // Allow same origin resource loads.
            'self',
            'https://static.ksp.sk/**'
        ]);

        $routeProvider.when('/series', {
            templateUrl: STATIC_URL_PREFIX + 'partials/series.html',
            controller: 'SeriesCtrl'
        });

        $routeProvider.when('/levels/:seriesId', {
            templateUrl: STATIC_URL_PREFIX + 'partials/levels.html',
            controller: 'LevelsCtrl',
            resolve: {
                factory: ['$q', '$rootScope', '$location', '$route',
                    function ($q, $rootScope, $location, $route) {
                        var deferred = $q.defer();

                        var seriesId = parseInt($route.current.params.seriesId);

                        if (isNaN(seriesId) || seriesId < 0 || seriesId >= $rootScope.series.length) {
                            $location.path('/');

                            deferred.reject();
                        }
                        else {
                            deferred.resolve();
                        }

                        return deferred.promise;
                    }]
            }
        });

        $routeProvider.when('/game/:levelId', {
            templateUrl: STATIC_URL_PREFIX + 'partials/game.html',
            controller: 'GameCtrl'
        });

        $routeProvider.otherwise({redirectTo: '/series'});
    }])
    .run(['$rootScope', 'Levels', function ($rootScope, Levels) {
        $rootScope.series = [];

        Levels({}).get(function (data) {
            $rootScope.series = data.series;
            $rootScope.player = data.player;
        }, function (data) {
            // Error
        });
    }]);
