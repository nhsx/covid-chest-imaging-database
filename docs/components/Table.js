export default function Table({ headings, rows }) {
   return (
      <div className="flex flex-col">
         <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
               <div className="overflow-hidden border-b border-gray-200">
                  <table className="min-w-full divide-y divide-gray-200">
                     <thead className="bg-white">
                        <tr>
                           {headings?.length > 0 && headings.map((heading, hIndex) => (
                              <th
                                 key={heading}
                                 scope="col"
                                 className={`px-6 py-3 text-left font-medium text-nhsuk-text ${hIndex == headings.length - 1 ? 'text-right' : ''}`}
                              >
                                 {heading}
                              </th>
                           ))}
                        </tr>
                     </thead>
                     <tbody>
                        {rows?.length > 0 && rows.map((row, rIndex) => (
                           <tr key={rIndex} className={`bg-white`}>
                              {row.map((column, cIndex) => (
                                 <td key={cIndex} className={`px-6 py-4 whitespace-nowrap text-nhsuk-text ${cIndex == headings?.length - 1 ? 'text-right' : ''}`}>{column}</td>
                              ))}
                           </tr>
                        ))}
                     </tbody>
                  </table>
               </div>
            </div>
         </div>
      </div>
   )
}