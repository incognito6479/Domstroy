// kassa_kirim start
var options = {
    series: [ {
        name: "Daromad",
        data: [27, 38, 49, 29, 42, 27, 60, 77, 40, 50, 42, 50]
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
            gradientToColors: ['#fff', '#fff', '#fff' ,'#fff'],
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
    colors: ["#ccc"],
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
var kassa_kirim = new ApexCharts(document.querySelector("#kassa_kirim"), options);
kassa_kirim.render();
// kassa_kirim end

