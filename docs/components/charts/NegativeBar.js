import { Bar } from 'react-chartjs-2';

export default function NegativeBar({ height, percentage, correct, incorrect }) {

   const data = {
      labels: ['People without Covid'],
      datasets: [
         {
            label: 'False Results',
            data: [incorrect],
            backgroundColor: '#d5281b'
         },
         {
            label: 'True Results',
            data: [correct],
            backgroundColor: '#005eb8'
         },
      ]
   }
   
   const options = {
      plugins: {
         title: {
            display: true,
            text: `True/False results in People without COVID FNs: ${percentage}% of all results`,
            font: {
               size: 14
            }
         },
      },
      responsive: true,
      scales: {
         x: {
            stacked: true,
         },
         y: {
            stacked: true
         }
      }
   }


   return <Bar height={height || 200} data={data} options={options} />
}