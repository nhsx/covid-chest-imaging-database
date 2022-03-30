import { Bar } from 'react-chartjs-2';

export default function StackedBarChart({ height, percentage, correct, incorrect, label, title }) {

   const labelColor = '#FFFFFF'
   const gridColor = 'rgba(255,255,255,0)'
   const lineColor = '#FFFFFF'
   const tickColor = '#FFFFFF'
   const positiveColor = '#70A5D7'
   const negativeColor = '#003567'

   const data = {
      labels: [label],
      datasets: [
         {
            label: 'False results',
            data: [incorrect],
            backgroundColor: negativeColor,
            borderColor: '#FFFFFF',
            fill: 'start'
         },
         {
            label: 'True results',
            data: [correct],
            backgroundColor: positiveColor,
            borderColor: '#FFFFFF',
            fill: 'start',
         },
      ]
   }

   const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
         legend: {
            labels: {
               color: labelColor,
               font: {
                  size: 14,
                  weight: 500
               }
            }
         },
         title: {
            display: false,
            text: title,
            font: {
               size: 14
            }
         },
      },
      scales: {
         x: {
            stacked: true,
            ticks: {
               display: false,
               color: tickColor,
            },
            grid: {
               borderColor: gridColor,
               borderWidth: 4,
               display: false,
               z: 1
            },
            title: {
               display: true,
               text: label,
               font: {
                  size: 14,
                  weight: 500
               },
               color: labelColor
            },
         },
         y: {
            stacked: false,
            ticks: {
               color: tickColor,
               beginAtZero: true,
            },
            grid: {
               borderColor: gridColor,
               borderWidth: 4,
               display: false,
               z: 1
            },
            title: {
               display: true,
               text: '% of all results',
               font: {
                  size: 14,
                  weight: 500
               },
               color: labelColor
            },
         }
      }
   }


   return <Bar className="flex-1" data={data} options={options} />
}