import { useEffect, useRef, useState } from "react"
import { Scatter } from 'react-chartjs-2'
import 'chart.js/auto';

export default function ROCLineChart({ height, plotData, fp, tp }) {

   // Colors 
   const labelColor = '#212b32'
   const gridColor = 'rgba(255,255,255,0)'
   const lineColor = '#005eb8'
   const tickColor = '#212b32'
   const intersectColor = 'rgba(0, 94, 184, .3)'

   // Load chart data into state so we can update later 
   const chartRef = useRef(null)
   const [chartData, setChartData] = useState({
      datasets: []
   })

   /**
    * On load, set gradient
    */
   useEffect(() => {
      const chart = chartRef.current;
      if (chart) {
         const gradient = chart.ctx.createLinearGradient(0, 0, 0, 300);
         gradient.addColorStop(0, 'rgba(0, 94, 184, .2)');
         gradient.addColorStop(1, 'rgba(0, 94, 184, 0)');
         setChartData({
            datasets: [
               {
                  label: 'X',
                  fill: false,
                  showLine: true,
                  pointRadius: 0,
                  data: [{ x: fp, y: 0 }, { x: fp, y: 1 }],
                  borderColor: intersectColor,
                  borderWidth: 2
               },
               {
                  label: 'Y',
                  fill: false,
                  showLine: true,
                  pointRadius: 0,
                  data: [{ x: 0, y: tp }, { x: 1, y: tp }],
                  borderColor: intersectColor,
                  borderWidth: 2,
               },
               {
                  label: 'Chance',
                  fill: false,
                  showLine: true,
                  pointRadius: 0,
                  data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
                  borderColor: intersectColor,
                  borderWidth: 2,
                  borderDash: [10, 4],
               },
               {
                  label: 'ROC Curve',
                  data: plotData,
                  fill: 'start',
                  showLine: true,
                  pointRadius: 0,
                  interpolate: true,
                  borderColor: lineColor,
                  backgroundColor: gradient,
                  cubicInterpolationMode: 'monotone',
                  tension: 0.4
               },
            ],
         });
      }
   }, [tp, fp]);


   const plugins = [
      {
         afterDraw: (chart) => {
            // eslint-disable-next-line no-underscore-dangle
            if (chart.tooltip._active && chart.tooltip._active.length) {
               // find coordinates of tooltip
               const activePoint = chart.tooltip._active[0];
               const { ctx } = chart;
               const { x } = activePoint.element;
               const topY = chart.scales.y.top;
               const bottomY = chart.scales.y.bottom;

               // draw vertical line
               ctx.save();
               ctx.beginPath();
               ctx.moveTo(x, topY);
               ctx.lineTo(x, bottomY);
               ctx.lineWidth = 1;
               ctx.strokeStyle = '#000000';
               ctx.stroke();
               ctx.restore();
            }
         },
      },
   ];

   const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
         mode: 'nearest',
         axis: 'x',
         intersect: false
      },
      plugins: {
         legend: {
            display: false,
            labels: {
               filter: function (label) {
                  if (label.text !== 'X' && label.text !== 'Y') return true;
               },
               color: labelColor
            }
         },
         title: {
            display: false,
            text: `Receiver Operating Characteristic (ROC)`,
            font: {
               size: 14
            },
            color: labelColor
         }
      },
      scales: {
         x: {
            beginAtZero: true,
            title: {
               display: true,
               text: 'FP Rate (1 - Specificity)',
               font: {
                  size: 14,
                  weight: 500
               },
               color: labelColor
            },
            ticks: {
               maxTicksLimit: 10,
               color: tickColor

            },
            grid: {
               borderColor: gridColor,
               borderWidth: 4,
               display: false,
               z: 1
            },
         },
         y: {
            beginAtZero: true,
            title: {
               display: true,
               text: 'TP Rate Sensitivity',
               font: {
                  size: 14,
                  weight: 500
               },
               color: labelColor
            },
            ticks: {
               maxTicksLimit: 10,
               color: tickColor
            },
            grid: {
               display: true,
               borderColor: gridColor,
               borderDash: [12, 4],
               borderWidth: 2,
               z: 1
            },
         }
      },
      animation: {
         duration: 0
      }
   }


   return <Scatter ref={chartRef} className="flex-1" data={chartData} options={chartOptions} plugins={plugins} />
}