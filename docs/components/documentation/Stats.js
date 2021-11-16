import { useEffect, useState } from "react"
import { parseFile } from "lib/csv"
import Table from "components/Table"

export default function Stats() {

   // Local state
   const [patientData, setPatientData] = useState(null)
   const [imageData, setImageData] = useState(null)
   const [storageData, setStorageData] = useState(null)
   const [submittingCentersData, setSubmittingCentersData] = useState(null)
   const [lastUpdated, setLastUpdated] = useState(null)

   // Get marker data, parse + store 
   const generateStats = async () => {
      setPatientData(await parseFile('/data/stats_patients.csv'))
      setImageData(await parseFile('/data/stats_images.csv'))
      setStorageData(await parseFile('/data/stats_storage.csv'))
      setSubmittingCentersData(await parseFile('/data/stats_submittingcentres.csv'))
      setLastUpdated(await parseFile('/data/stats_date.txt'))
   }

   // On load, get markers
   useEffect(() => {
      generateStats()
   }, [])

   // Output table 
   const outputDataTable = (data) => {
      const copy = [...data]
      const headings = copy.shift()
      return <Table headings={headings} rows={copy} />
   }

   return (
      <div className="space-y-6">
         {/* Data */}
         {patientData && outputDataTable(patientData)}
         {imageData && outputDataTable(imageData)}
         {storageData && outputDataTable(storageData)}
         {submittingCentersData && outputDataTable(submittingCentersData)}

         {/* Last updated */}
         {lastUpdated && (
            <p className="text-nhsuk-secondary-text">
               <i>{lastUpdated[0]}</i>
            </p>
         )}
      </div>
   )
}