import Annotation from 'chartjs-plugin-annotation'
import { Bar, Chart } from 'react-chartjs-2'

Chart.register(Annotation)

export default function AccuracyChart({ barData, barLabels, lineData, xLabel, yLabel }) {

   const labelColor = '#FFFFFF'
   const lineColor = '#FFFFFF'
   const tickColor = '#FFFFFF'
   const barColour = 'rgba(255,255,255,0.5)'
   const borderColor = '#FFFFFF'

   const data = (canvas) => {
      return {
         labels: barLabels,
         datasets: [
            {
               label: xLabel,
               data: barData,
               backgroundColor: barColour,
               borderColor: borderColor,
               borderWidth: 2
            },
         ],
      }
   }

   const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
         legend: {
            display: false
         },
         title: {
            display: false,
         },
         annotation: {
            annotations: [{
               drawTime: 'afterDatasetsDraw',
               borderColor: '#FFF',
               borderDash: [12, 4],
               borderWidth: 2,
               mode: 'horizontal',
               type: 'line',
               yMin: 80,
               yMax: 80,
               scaleID: 'y-axis-0',
            }]
         }
      },
      scales: {
         x: {
            ticks: {
               display: true,
               color: tickColor,
               font: {
                  size: 14,
                  weight: 500
               },
            },
            grid: {
               borderColor: lineColor,
               borderWidth: 4,
               display: false,
               z: 1
            },
            title: {
               display: true,
               text: xLabel,
               font: {
                  size: 21,
                  weight: 700
               },
               color: labelColor
            },
         },
         y: {
            ticks: {
               display: false,
               color: tickColor,
               beginAtZero: true,
               min: 0,
               max: 100,
               stepSize: 20
            },
            grid: {
               borderColor: lineColor,
               borderWidth: 4,
               drawBorder: false,
               display: false,
               z: 1
            },
            title: {
               display: yLabel,
               text: yLabel,
               font: {
                  size: 21,
                  weight: 700
               },
               color: labelColor
            },
         }
      }
   }


   return <Bar className="flex-1" data={data} options={options} />
}