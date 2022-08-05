'use strict';

// Note the space at the end of URLs is a hack.
// https://stackoverflow.com/questions/14533117/angular-trailing-slash-for-resource

angular.module('zerg.services', [])
    .factory('Levels', ['$resource', function($resource) {
        return function(customHeaders) {
        	return $resource(DYNAMIC_URL_PREFIX + 'levels/:levelId/ ', {}, {
        		'get': {
        			headers: customHeaders || {}
        		},
        		'submitLevel': {
        			method: 'POST',
        			headers: customHeaders || {}
        		}
        	});
        };
    }])
    .factory('Solutions', ['$resource', function($resource) {
        return function(customHeaders) {
            return $resource(DYNAMIC_URL_PREFIX + 'solutions/:levelId/ ', {}, {
                'get': {
                    transformResponse: function(data, headersGetter) {
                        return {solution: data};
                    },
                    headers: customHeaders || {}
                }
            });
        };
    }])
    .factory('Submits', ['$resource', function($resource) {
        return function(customHeaders) {
            return $resource(DYNAMIC_URL_PREFIX + 'submits/:submitId/ ', {}, {
                'get': {
                    headers: customHeaders || {}
                }
            });
        };
    }]);
