/*
$(function () {
	"use strict";

	// chart 1 start
	var options = {
		series: [{
			name: 'Sessions',
			data: [427, 613, 901, 257, 505, 414, 671, 160, 440]
		}],
		chart: {
			type: 'area',
			height: 80,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: true,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.12,
				color: '#000',
			},
			sparkline: {
				enabled: true
			}
		},
		markers: {
			size: 0,
			colors: ["#000"],
			strokeColors: "#fff",
			strokeWidth: 2,
			hover: {
				size: 7,
			}
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		colors: ["#ffffff"],
		xaxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		},
		fill: {
			opacity: 1
		},
		tooltip: {
			theme: 'dark',
			fixed: {
				enabled: false
			},
			x: {
				show: false
			},
			y: {
				title: {
					formatter: function (seriesName) {
						return ''
					}
				}
			},
			marker: {
				show: false
			}
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart1"), options);
	chart.render();
	// chart 1 end

	// chart 2 start
	var options = {
		series: [{
			name: 'Visitors',
			data: [427, 613, 901, 257, 505, 414, 671, 160, 440]
		}],
		chart: {
			type: 'area',
			height: 80,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: true,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.12,
				color: '#000',
			},
			sparkline: {
				enabled: true
			}
		},
		markers: {
			size: 0,
			colors: ["#000"],
			strokeColors: "#fff",
			strokeWidth: 2,
			hover: {
				size: 7,
			}
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		colors: ["#ffffff"],
		xaxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		},
		fill: {
			opacity: 1
		},
		tooltip: {
			theme: 'dark',
			fixed: {
				enabled: false
			},
			x: {
				show: false
			},
			y: {
				title: {
					formatter: function (seriesName) {
						return ''
					}
				}
			},
			marker: {
				show: false
			}
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart2"), options);
	chart.render();
	// chart 2 end

	// chart 3 start
	var options = {
		series: [{
			name: 'Page Views',
			data: [427, 613, 901, 257, 505, 414, 671, 160, 440]
		}],
		chart: {
			type: 'area',
			height: 80,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: true,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.12,
				color: '#000',
			},
			sparkline: {
				enabled: true
			}
		},
		markers: {
			size: 0,
			colors: ["#000"],
			strokeColors: "#fff",
			strokeWidth: 2,
			hover: {
				size: 7,
			}
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		colors: ["#ffffff"],
		xaxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		},
		fill: {
			opacity: 1
		},
		tooltip: {
			theme: 'dark',
			fixed: {
				enabled: false
			},
			x: {
				show: false
			},
			y: {
				title: {
					formatter: function (seriesName) {
						return ''
					}
				}
			},
			marker: {
				show: false
			}
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart3"), options);
	chart.render();
	// chart 3 end

	// chart 4 start
	var options = {
		series: [{
			name: 'Oldi',
			data: [18, 51, 80, 38, 88, 50, 40, 52, 88, 80, 60, 70]
		}, {
			name: 'Sotdi',
			data: [27, 38, 60, 77, 40, 50, 49, 29, 42, 27, 42, 50]
		}],
		chart: {
			foreColor: 'rgba(255, 255, 255, 0.65)',
			type: 'area',
			height: 273,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: false,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.10,
			}
		},
		legend: {
			position: 'top',
			horizontalAlign: 'left',
			offsetX: -25
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		tooltip: {
			theme: 'dark',
			y: {
				formatter: function (val) {
					return "$ " + val + " "
				}
			}
		},
		fill: {
			type: 'gradient',
			gradient: {
				shade: 'light',
				gradientToColors: ['#fff', 'rgba(255, 255, 255, 0.65)'],
				shadeIntensity: 1,
				type: 'vertical',
				inverseColors: false,
				opacityFrom: 0.4,
				opacityTo: 0.1,
				//stops: [0, 50, 65, 91]
			},
		},
		grid: {
			show: true,
			borderColor: 'rgba(255, 255, 255, 0.12)',
			strokeDashArray: 5,
		},
		colors: ["#fff", "rgba(255, 255, 255, 0.65)"],
		yaxis: {
			labels: {
				formatter: function (value) {
					return value + "$";
				}
			},
		},
		xaxis: {
			categories: ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyun', 'Iyul', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'],
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart4"), options);
	chart.render();
	// chart 4 end

	// charr 5 start
	var options = {
		series: [{
			name: 'Page Views',
			data: [427, 613, 901, 257, 505, 414, 671, 160, 440]
		}],
		chart: {
			type: 'area',
			height: 80,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: true,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.12,
				color: '#000',
			},
			sparkline: {
				enabled: true
			}
		},
		markers: {
			size: 0,
			colors: ["#000"],
			strokeColors: "#fff",
			strokeWidth: 2,
			hover: {
				size: 7,
			}
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		colors: ["#ffffff"],
		xaxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		},
		fill: {
			opacity: 1
		},
		tooltip: {
			theme: 'dark',
			fixed: {
				enabled: false
			},
			x: {
				show: false
			},
			y: {
				title: {
					formatter: function (seriesName) {
						return ''
					}
				}
			},
			marker: {
				show: false
			}
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart5"), options);
	chart.render();
	// chart 5 end

	// charr 6 start
	var options = {
		series: [{
			name: 'Page Views',
			data: [427, 613, 901, 257, 505, 414, 671, 160, 440]
		}],
		chart: {
			type: 'area',
			height: 80,
			toolbar: {
				show: false
			},
			zoom: {
				enabled: false
			},
			dropShadow: {
				enabled: true,
				top: 3,
				left: 14,
				blur: 4,
				opacity: 0.12,
				color: '#000',
			},
			sparkline: {
				enabled: true
			}
		},
		markers: {
			size: 0,
			colors: ["#000"],
			strokeColors: "#fff",
			strokeWidth: 2,
			hover: {
				size: 7,
			}
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 3,
			curve: 'smooth'
		},
		colors: ["#ffffff"],
		xaxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
		},
		fill: {
			opacity: 1
		},
		tooltip: {
			theme: 'dark',
			fixed: {
				enabled: false
			},
			x: {
				show: false
			},
			y: {
				title: {
					formatter: function (seriesName) {
						return ''
					}
				}
			},
			marker: {
				show: false
			}
		}
	};
	var chart = new ApexCharts(document.querySelector("#chart6"), options);
	chart.render();
	// chart 6 end

});*/
