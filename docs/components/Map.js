import L from 'leaflet'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

import 'leaflet/dist/leaflet.css'


export default function Map({ position, markers = [], zoom = 8, markerSize = 8 }) {
   return (
      <MapContainer center={position} zoom={zoom} scrollWheelZoom={false} className="w-full h-[450px]">
         <TileLayer
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
         />
         {
            markers.map(({ title, lat, lng }) => (
               <Marker
                  key={title}
                  position={{ lat, lng }}
                  icon={L.divIcon({
                     iconSize: [markerSize, markerSize],
                     iconAnchor: [markerSize / 2, - markerSize * 2],
                     className: "bg-blue-500 rounded-full",
                  })}
               >
                  <Popup>
                     {title}
                  </Popup>
               </Marker>
            ))
         }
      </MapContainer>
   )
}