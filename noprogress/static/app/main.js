(function () {
    "use strict";

    var noprogress = angular.module("noprogress", [], function($interpolateProvider) {
        $interpolateProvider.startSymbol("<%=");
        $interpolateProvider.endSymbol("%>");
    });

    noprogress.filter("reprSets", function () {
        return function (sets) {
            if (!sets) return "";
            return sets.map(function (set) { return set.weight + "kg/" + set.reps; }).join("\n");
        };
    });

    noprogress.controller("WorkoutCtrl", function ($scope, $http) {
        $http({method: "GET", url: "/api/workouts"}).
            success(function (data, status, headers, config) {
                var workouts = data.workouts;

                workouts.forEach(function (workout) {
                    workout.liftSetsMap = {};
                    workout.lifts.forEach(function (lift) {
                        var liftName = lift.name.replace(/_[a-z]/g, function (x) {
                            return x[1].toUpperCase();
                        });
                        workout.liftSetsMap[liftName] = lift.sets;
                    });
                });

                $scope.workouts = workouts;
            });
    });
})();
