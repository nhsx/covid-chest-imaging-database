import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'
import { parseFile } from 'lib/csv'

const Map = dynamic(
   () => import('../Map'),
   { ssr: false }
)
const position = { lat: 54.5, lng: -5 }
const markers = [
   {
      title: 'Location 1',
      lat: '52.429222',
      lng: '-1.433558'
   },
   {
      title: 'Location 2',
      lat: '52.375599',
      lng: '-0.892208'
   },
   {
      title: 'Location 3',
      lat: '51.426614',
      lng: '-1.551828'
   },
   {
      title: 'Location 4',
      lat: '54.188155',
      lng: '-0.716310'
   },
]

export default function LocationsMap() {

   // Local storage 
   const [markers, setMarkers] = useState(null)

   // Get marker data, parse + store 
   const generateMarkers = async () => {

      // Parse file 
      const data = await parseFile('/data/hospital_locations.csv')

      // Remove headers
      data.shift()

      // Set data
      setMarkers(data.map(entry => ({
         title: entry[0],
         lat: entry[1],
         lng: entry[2]
      })))

   }

   // On load, get markers
   useEffect(() => {
      generateMarkers()
   }, [])

   return (
      <div className="mt-12 mb-6">
         {markers ? <Map markers={markers} position={position} zoom={5} /> : null}
      </div>
   )
}