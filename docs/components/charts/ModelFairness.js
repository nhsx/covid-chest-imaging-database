import AccuracyChart from "./parts/AccuracyChart";

export default function ModelFairness() {
   return (
      <>

         {/* Main panel */}
         <div className="h-full flex flex-col items-center justify-center pb-12">

            <div className="mb-12">
               <h2 className="text-white text-3xl 2xl:text-5xl font-bold"><span className="text-blue-200">Model Fairness:</span> 80%</h2>
            </div>

            <div className="flex-1 grid lg:grid-cols-3 gap-10 h-full w-full lg:max-w-[1600px] lg:max-h-[500px] 2xl:max-h-[600px] mx-auto py-12">

               <div className="flex flex-col">
                  <div className="flex items-stretch flex-1">
                     <AccuracyChart barData={[70, 90]} barLabels={['Male', 'Female']} xLabel="Gender" yLabel="Accuracy" />
                  </div>
               </div>

               <div className="flex flex-col">
                  <div className="flex items-stretch flex-1">
                     <AccuracyChart barData={[83, 75]} barLabels={['Under 65', 'Over 65']} xLabel="Age" />
                  </div>
               </div>

               <div className="flex flex-col">
                  <div className="flex items-stretch flex-1">
                     <AccuracyChart barData={[65, 81, 92, 80]} barLabels={['W', 'B', 'B', 'O']} xLabel="Ethnicity" />
                  </div>
               </div>

            </div>

         </div>


      </>

   )
}