(function () {
    "use strict";

    var noprogress = angular.module("noprogress", [], function($interpolateProvider) {
        $interpolateProvider.startSymbol("<%=");
        $interpolateProvider.endSymbol("%>");
    });

    noprogress.factory("strStd", function () {
        function wathan(w, r) {
            return 100 * w / (48.8 + 53.8 * Math.pow(Math.E, -0.075 * r));
        }

        function lbToKg(lb) {
            return lb / 2.20462;
        }

        function kgToLb(kg) {
            return kg * 2.20462;
        }

        function calculateGrades(sex, lift, bw) {
            var table = tables[sex][lift];

            for (var i = 0; i < table.length; ++i) {
                var bwLimit = lbToKg(table[i][0]);
                if (bw < bwLimit) {
                    var bits = table[i].slice(1).map(lbToKg);
                    return {
                        untrained: bits[0],
                        novice: bits[1],
                        intermediate: bits[2],
                        advanced: bits[3],
                        elite: bits[4]
                    };
                }
            }
        }

        // These tables are taken from:
        // http://push-hard.blogspot.com/2009/10/basic-strength-standards-for-adult-men.html
        // http://push-hard.blogspot.com/2009/10/basic-strength-standards-for-adult.html
        var tables = {
            male: {
                overhead_press:
                [[114, 53, 72, 90, 107, 129],
                 [123, 57, 78, 98, 116, 141],
                 [132, 61, 84, 105, 125, 151],
                 [148, 69, 94, 119, 140, 169],
                 [165, 75, 102, 129, 153, 186],
                 [181, 81, 110, 138, 164, 218],
                 [198, 85, 116, 146, 173, 234],
                 [220, 89, 122, 155, 183, 255],
                 [242, 93, 127, 159, 189, 264],
                 [275, 96, 131, 164, 194, 272],
                 [319, 98, 133, 167, 199, 278],
                 [Infinity, 100, 136, 171, 203, 284]],

                bench_press:
                [[114, 84, 107, 130, 179, 222],
                 [123, 91, 116, 142, 194, 242],
                 [132, 98, 125, 153, 208, 260],
                 [148, 109, 140, 172, 234, 291],
                 [165, 119, 152, 187, 255, 319],
                 [181, 128, 164, 201, 275, 343],
                 [198, 135, 173, 213, 289, 362],
                 [220, 142, 183, 225, 306, 381],
                 [242, 149, 190, 232, 316, 395],
                 [275, 153, 196, 239, 325, 407],
                 [319, 156, 199, 244, 333, 416],
                 [Infinity, 159, 204, 248, 340, 425]],

                squat:
                [[114, 78, 144, 174, 240, 320],
                 [123, 84, 155, 190, 259, 346],
                 [132, 91, 168, 205, 278, 369],
                 [148, 101, 188, 230, 313, 410],
                 [165, 110, 204, 250, 342, 445],
                 [181, 119, 220, 269, 367, 479],
                 [198, 125, 232, 285, 387, 504],
                 [220, 132, 244, 301, 409, 532],
                 [242, 137, 255, 311, 423, 551],
                 [275, 141, 261, 319, 435, 567],
                 [319, 144, 267, 326, 445, 580],
                 [Infinity, 147, 272, 332, 454, 593]],

                deadlift:
                [[114, 97, 179, 204, 299, 387],
                 [123, 105, 194, 222, 320, 414],
                 [132, 113, 209, 239, 342, 438],
                 [148, 126, 234, 269, 380, 482],
                 [165, 137, 254, 293, 411, 518],
                 [181, 148, 274, 315, 438, 548],
                 [198, 156, 289, 333, 457, 567],
                 [220, 164, 305, 351, 479, 586],
                 [242, 172, 318, 363, 490, 596],
                 [275, 176, 326, 373, 499, 602],
                 [319, 180, 333, 381, 506, 608],
                 [Infinity, 183, 340, 388, 512, 617]],

                power_clean:
                [[114, 56, 103, 125, 173, 207],
                 [123, 60, 112, 137, 186, 224],
                 [132, 65, 121, 148, 200, 239],
                 [148, 73, 135, 166, 225, 266],
                 [165, 79, 147, 180, 246, 288],
                 [181, 85, 158, 194, 264, 310],
                 [198, 90, 167, 205, 279, 327],
                 [220, 95, 176, 217, 294, 345],
                 [242, 99, 183, 224, 305, 357],
                 [275, 102, 188, 230, 313, 367],
                 [319, 104, 192, 235, 320, 376],
                 [Infinity, 106, 196, 239, 327, 384]]
            }
         };

        return {
            wathan: wathan,
            tables: tables,
            calculateGrades: calculateGrades,
            kgToLb: kgToLb,
            lbToKg: lbToKg
        };
    });

    noprogress.filter("reprSets", function () {
        return function (sets) {
            if (!sets) return "";
            return sets.map(function (set) { return set.weight + "kgx" + set.reps; }).join("<br>");
        };
    });

    noprogress.controller("StrStdCtrl", function ($scope, $http, strStd) {
        $scope.bodyweight = 70;
        $scope.gender = "male";

        $scope.grades = {};
        $scope.onerms = {};
        $scope.percents = {};

        $http({
            method: "GET",
            url: "/api/last"
        }).
            success(function (data, status, headers, config) {
                $scope.last = data;
                Object.keys(data).forEach(function (k) {
                    var v = data[k][0];
                    $scope.onerms[k] = strStd.wathan(v.weight, v.reps);
                    $scope.grades[k] = strStd.calculateGrades($scope.gender, k, $scope.bodyweight);
                    $scope.percents[k] = {};

                    Object.keys($scope.grades[k]).forEach(function (l) {
                        $scope.percents[k][l] = Math.min(100, Math.round($scope.onerms[k] * 100 / $scope.grades[k][l]));
                    });
                });
                console.log($scope.percents);
            });
    });

    noprogress.controller("LogWorkoutCtrl", function ($rootScope, $scope, $http) {
        $scope.doLog = function () {
            $http({
                method: "POST",
                url: "/api/log",
                data: {log: $scope.log}
            }).
                success(function (data, status, headers, config) {
                    $rootScope.$broadcast("workouts.updated");
                    $scope.log = "";
                });
        };
    });

    noprogress.controller("WorkoutsCtrl", function ($scope, $http) {
        $scope.limit = 5;
        $scope.currentPage = 1;

        $scope.goToPage = function (page) {
            $scope.currentPage = page;
            $scope.$emit("workouts.updated");
        };

        $scope.refresh = function () {
            $http({
                method: "GET",
                url: "/api/workouts",
                params: {
                    offset: ($scope.currentPage - 1) * $scope.limit,
                    limit: $scope.limit
                }
            }).
                success(function (data, status, headers, config) {
                    var workouts = data.workouts;

                    workouts.forEach(function (workout) {
                        workout.liftSetsMap = {};
                        workout.lifts.forEach(function (lift) {
                            workout.liftSetsMap[lift.name] = lift.sets;
                        });
                    });

                    $scope.workouts = workouts;
                    $scope.totalPages = Math.ceil(data.total / $scope.limit);

                    $scope.pages = [];

                    for (var i = 1; i <= $scope.totalPages; ++i) {
                        $scope.pages.push(i);
                    }
                });
        };
        $scope.refresh();
        $scope.$on("workouts.updated", $scope.refresh);
    });
})();
