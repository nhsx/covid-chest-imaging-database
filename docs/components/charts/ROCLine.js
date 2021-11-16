import { Scatter } from 'react-chartjs-2';
import { CrosshairPlugin, Interpolate } from 'chartjs-plugin-crosshair';

export default function ROCLine({ height, plotData, fp, tp }) {

   const data = {
      datasets: [
         {
            label: 'X',
            fill: false,
            showLine: true,
            pointRadius: 0,
            data: [{ x: fp, y: 0 }, { x: fp, y: 1 }],
            borderColor: 'rgba(0, 0, 0, 0.4)',
         },
         {
            label: 'Y',
            fill: false,
            showLine: true,
            pointRadius: 0,
            data: [{ x: 0, y: tp }, { x: 1, y: tp }],
            borderColor: 'rgba(0, 0, 0, 0.4)',
         },
         {
            label: 'ROC Curve',
            data: plotData,
            fill: false,
            showLine: true,
            pointRadius: 0,
            lineTension: 0,
            interpolate: true,
            borderColor: '#005eb8',
         },
      ],
   }

   const options = {
      plugins: {
         legend: {
            labels: {
               filter: function (label) {
                  if (label.text !== 'X' && label.text !== 'Y') return true;
               }
            }
         },
         title: {
            display: true,
            text: `Receiver Operating Characteristic (ROC)`,
            font: {
               size: 14
            }
         },
         crosshair: {
            zoom: {
               enabled: false
            }
         }
      },
      scales: {
         x: {
            title: {
               display: true,
               text: 'FP Rate (1 - Specificity)',
            },
            beginAtZero: true,
            ticks: {
               maxTicksLimit: 10
            }
         },
         y: {
            title: {
               display: true,
               text: 'TP Rate Sensitivity',
            },
            beginAtZero: true,
            ticks: {
               maxTicksLimit: 10
            }
         }
      },
      animation: {
         duration: 0
      }
   }


   return <Scatter height={height || 400} data={data} options={options} plugins={[CrosshairPlugin]} />
}