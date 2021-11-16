import { Bar, Pie } from 'react-chartjs-2';

export default function PieChart({ labels, values, colors }) {

   const gridColor = 'rgba(255,255,255,0)'
   const labelColor = '#FFFFFF'
   const positiveColor = '#70A5D7'
   const negativeColor = '#003567'
   const blankColor = '#FFFFFF'

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
         legend: {
            labels: {
               color: labelColor,
               font: {
                  size: 14,
                  weight: 500
               }
            }
         },
      },
   }


   return <Pie className="flex-1" data={data} options={options} />
}