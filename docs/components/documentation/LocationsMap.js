import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'
import { parseFile } from 'lib/csv'

const Map = dynamic(
   () => import('../Map'),
   { ssr: false }
)
const position = { lat: 54.5, lng: -5 }

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