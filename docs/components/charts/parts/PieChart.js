import { Bar, Doughnut, Pie } from 'react-chartjs-2';

export default function PieChart({ labels, values, colors }) {

   const gridColor = 'rgba(255,255,255,0)'
   const labelColor = '#212b32'
   const positiveColor = '#005eb8'
   const negativeColor = '#007f3b'
   const blankColor = '#d2d8dc'

   const data = (canvas) => {
      return {
         labels,
         datasets: [
            {
               label: 'Results with Covid',
               data: values,
               backgroundColor: [blankColor, negativeColor, positiveColor]
            },
         ]
      }
   }

   const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
         tooltip: {
            callbacks: {
               label: function (tooltipItem) {
                  return ' ' + tooltipItem.formattedValue + '%'
               },
               title: function(tooltipItem) {
                  return tooltipItem[0].label
                }
            }
         },
         legend: {
            labels: {
               color: labelColor,
               font: {
                  size: 14,
                  weight: 500
               }
            }
         }
      },
   }


   return <Doughnut className="flex-1" data={data} options={options} />
}