import { Range } from 'react-range';
import { useEffect, useMemo, useState } from 'react';
import { parseFile } from 'lib/csv';
import StackedBarChart from './parts/StackedBarChart';
import ROCLineChart from 'components/charts/parts/ROCLineChart';
import Modal from 'components/Modal';
import Button from 'components/Button';
import PieChart from './parts/PieChart';

const ChartTitle = ({ children }) => (
   <div className="flex justify-center lg:justify-start w-full mb-6">
      <div className="bg-black bg-opacity-10 px-4 py-1 rounded-full shadow-inner">
         <h3 className="text-white font-semibold text-center">{children}</h3>
      </div>
   </div>
)

const StatOutput = ({ title, value }) => (
   <div className="px-6 py-3">
      <dt className="text-sm font-medium text-blue-100 truncate">{title}</dt>
      <dd className="text-lg font-semibold text-white">{parseFloat(value).toFixed(2)}%</dd>
   </div>
)

const GlossaryRow = ({ title, description }) => (
   <div className="grid sm:grid-cols-12 gap-2 text-nhsuk-text">
      <dt className="sm:col-span-3 font-medium">{title}</dt>
      <dd className="sm:col-span-9">{description}</dd>
   </div>
)

const ControlRange = ({ step, min, max, value, onChange }) => (
   <Range
      step={step}
      min={min}
      max={max}
      values={[value]}
      onChange={onChange}
      renderTrack={({ props, children }) => (
         <div
            {...props}
            className="h-1 bg-blue-400 rounded-full"
         >
            {children}
         </div>
      )}
      renderThumb={({ props }) => (
         <div
            {...props}
            className="w-4 h-4 bg-white shadow rounded-full"
         />
      )}
   />
)

export default function OperatingPoint() {

   // Local state
   const [percentage, setPercentage] = useState(5)
   const [operatingPoint, setOperatingPoint] = useState(0.4)
   const [rocData, setRocData] = useState(null)
   const [statsOpen, setStatsOpen] = useState(false)
   const [glossaryOpen, setGlossaryOpen] = useState(false)
   const [breakdownOpen, setBreakdownOpen] = useState(false)

   // Calculate nearest operating point 
   const nearestOperatingPoint = useMemo(() => rocData && rocData.find(point => parseFloat(point.operatingPoint).toFixed(2) - operatingPoint < 0.01), [rocData, operatingPoint])

   // Specific calculations 
   const { x, y } = nearestOperatingPoint || { x: 0, y: 0 }
   const tp = y
   const fp = x
   const sensitivity = tp
   const specificity = 1 - fp
   const prevalance = (percentage / 100)
   const npv = operatingPoint == 0 ? 'N/A' : (specificity * (1 - prevalance)) / ((specificity * (1 - prevalance)) + ((1 - sensitivity) * prevalance))
   const ppv = operatingPoint == 1 ? 'N/A' : (sensitivity * prevalance) / ((sensitivity * prevalance) + ((1 - specificity) * (1 - prevalance)))
   const tp_final = sensitivity * percentage
   const tn_final = specificity * (100 - percentage)
   const fn_final = (1 - sensitivity) * percentage
   const fp_final = (1 - specificity) * (100 - percentage)
   const accuracy = (tp_final + tn_final)

   // Generate ROC data 
   const generateRocData = async () => {

      // Parse file 
      let data = await parseFile('/data/roc_data.csv')

      // Remove headers
      data.shift()

      // Only keep fp & tp
      data = data.map(point => ({
         x: point[1],
         y: point[2],
         operatingPoint: point[3]
      }))

      // Store data
      setRocData(data)

   }

   // On load, get data 
   useEffect(() => {
      generateRocData()
   }, [])

   return (
      <>

         {/* Main panel */}
         <div className="h-full flex flex-col items-center justify-center">

            <div className="mb-6 2xl:mb-12 text-center">
               <h2 className="text-white text-xl sm:text-3xl xl:text-4xl 2xl:text-5xl font-bold"><span className="text-blue-200">Operating Point:</span> {parseFloat(operatingPoint).toFixed(2)}</h2>
               <p className="text-lg text-blue-200 mt-4 px-6">Choose an Operating Point for the model and a prevalence of COVID in the population of interest then see the results below:</p>
            </div>

            {/* Output */}
            <div className="w-full sm:border sm:border-blue-600 sm:bg-white sm:bg-opacity-5 sm:rounded-xl sm:shadow-inner lg:max-w-[1600px] mx-auto mb-6">
               <div className="flex flex-col sm:p-6 xl:flex-row xl:justify-between xl:items-center">

                  {/* Controls */}
                  <div className="grid sm:grid-cols-2 gap-6 text-white">
                     <div>
                        <div className="flex justify-between space-x-6 items-center mb-3">
                           <div>
                              <label className="font-medium">Operating point</label>
                           </div>
                           <div>
                              <span className="text-sm text-blue-100">{parseFloat(operatingPoint).toFixed(2)}</span>
                           </div>
                        </div>
                        <ControlRange min={0} max={1} step={0.01} value={operatingPoint} onChange={(value) => setOperatingPoint(value || operatingPoint)} />
                     </div>
                     <div>
                        <div className="flex justify-between space-x-6 items-center mb-3">
                           <div>
                              <label className="font-medium">Prevalence <span className="text-sm text-blue-200">(% of population with COVID)</span>:</label>
                           </div>
                           <div>
                              <span className="text-sm text-blue-100">{percentage}%</span>
                           </div>
                        </div>
                        <ControlRange min={0} max={100} step={1} value={percentage} onChange={(value) => setPercentage(value || percentage)} />
                     </div>
                  </div>


                  {/* Helpers */}
                  <div className="flex flex-col space-x-0 space-y-4 sm:flex-row sm:justify-center sm:space-x-4 sm:space-y-0 mt-10 xl:mt-0 xl:justify-end">
                     <div className="flex-1 sm:flex-auto">
                        <Button onClick={() => setBreakdownOpen(true)} fullwidth>
                           What does this data mean?
                        </Button>
                     </div>
                     <div className="flex-1 sm:flex-auto">
                        <Button onClick={() => setGlossaryOpen(true)} color="white" fullwidth>
                           View glossary
                        </Button>
                     </div>
                  </div>

               </div>
            </div>


            <div className="flex flex-col w-full lg:max-w-[1600px] mx-auto sm:bg-black sm:bg-opacity-5 sm:rounded-xl sm:shadow-inner sm:overflow-hidden">

               <div className="flex-1 grid lg:grid-cols-4 lg:divide-x lg:divide-blue-500">

                  {/* ROC */}
                  <div className="lg:col-span-4 xl:col-span-2 flex flex-col my-8 sm:px-8 sm:my-10 lg:mb-0 xl:my-10">
                     <div>
                        <ChartTitle>ROC Curve</ChartTitle>
                     </div>
                     <div className="flex items-stretch flex-1">
                        <ROCLineChart plotData={rocData} fp={fp} tp={tp} />
                     </div>
                  </div>

                  {/* Positive */}
                  <div className="lg:col-span-2 xl:col-span-1 flex flex-col my-8 sm:px-8 sm:my-10">
                     <div>
                        <ChartTitle>Results in people with COVID</ChartTitle>
                     </div>
                     <div className="flex items-stretch flex-1">
                        <PieChart labels={['Negative', 'FN', 'TP']} values={[100 - tp_final - fn_final, fn_final, tp_final]} />
                        {/* <StackedBarChart title={`Results in People with COVID FNs: ${percentage}% of all results`} label="People with Covid" percentage={percentage} correct={tp_final} incorrect={fn_final} /> */}
                     </div>
                  </div>

                  {/* Negative */}
                  <div className="lg:col-span-2 xl:col-span-1 flex flex-col my-8 sm:px-8 sm:my-10">
                     <div>
                        <ChartTitle>Results in people without COVID</ChartTitle>
                     </div>
                     <div className="flex items-stretch flex-1">
                        <PieChart labels={['Positive', 'FP', 'TN']} values={[100 - fp_final - tn_final, fp_final, tn_final]} />
                        {/* <StackedBarChart title={`Results in People without COVID FNs: ${percentage}% of all results`} label="People without Covid" percentage={percentage} correct={tn_final} incorrect={fp_final} /> */}
                     </div>
                  </div>


               </div>

               <div className="flex justify-center bg-black bg-opacity-10 py-3">
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 xl:w-auto xl:flex xl:flex-wrap">
                     <StatOutput title="TP" value={tp_final} />
                     <StatOutput title="TN" value={tn_final} />
                     <StatOutput title="FP" value={fp_final} />
                     <StatOutput title="FN" value={fn_final} />
                     <StatOutput title="Sensitivity" value={sensitivity * 100} />
                     <StatOutput title="Specificity" value={specificity * 100} />
                     <StatOutput title="Raw Accuracy" value={accuracy} />
                     <StatOutput title="PPV" value={ppv * 100} />
                     <StatOutput title="NPV" value={npv * 100} />
                  </div>
               </div>

            </div>

         </div>

         {/* Glossary */}
         <Modal show={glossaryOpen} onClose={() => setGlossaryOpen(false)} title="Glossary" content={(
            <dl className="text-sm text-nhsuk-text space-y-4">
               <GlossaryRow title="Sensitivity:" description="Proportion of positive cases that are correctly predicted to be positive." />
               <GlossaryRow title="Specificity:" description="Proportion of negative cases that are correctly predicted to be negative." />
               <GlossaryRow title="Raw Accuracy:" description="Proportion of all cases that are correctly predicted (i.e. TP and TN)" />
               <GlossaryRow title="True Positive (TP):" description="Model correctly predicts the positive class (i.e. model predicts that a patient with Covid-19 has Covid-19)" />
               <GlossaryRow title="False Positive (FP):" description="Model incorrectly predicts the positive class (i.e. model predicts that a patient has Covid-19, when in fact the patient does not have Covid-19)." />
               <GlossaryRow title="True Negative (TN):" description="Model correctly predicts the negative class (i.e. model predicts that a patient who does not have Covid-19, doesn&rsquo;t have Covid-19)." />
               <GlossaryRow title="False Negative (FN):" description="Model incorrectly predicts the negative class (i.e. model predicts that a patient doesn&rsquo;t have Covid-19, when in fact the patient does have Covid-19)." />
               <GlossaryRow title="Positive Predictive Value (PPV):" description="Probability a case is truly positive (i.e. positive Covid-19 diagnosis), given it is predicted positive by the model." />
               <GlossaryRow title="Negative Predictive Value (NPV):" description="Probability a case is truly negative (i.e. negative Covid-19 diagnosis), given it is predicted negative by the model." />
               <GlossaryRow title="True Positive Rate:" description="Proportion of positive cases correctly predicted to be positive. Equivalent to Sensitivity." />
               <GlossaryRow title="False Positve Rate:" description="Proportion of negative cases incorrectly predicted to be positive. Equivalent to (1 - Specificity)." />
               <GlossaryRow title="ROC Curve:" description="Receiver Operator Characteristic Curve. A plotted curve which demonstrates how the trade off between True Positive Rate and False Positive Rate changes as you vary the operating point of the model." />
            </dl>
         )} />

         {/* Breakdown */}
         <Modal show={breakdownOpen} onClose={() => setBreakdownOpen(false)} title="Within all people the model tests..." content={(
            <div className="text-nhsuk-text text-sm">
               <p>{(tp_final + fp_final).toFixed(2)}% of them will be predicted to have a COVID infection (aka TPs + FPs).</p>
               <p>{(fn_final).toFixed(2)}% of them will both truely have a COVID infection and be told they do not have one (aka will be FNs).</p>
               <p>{(fp_final).toFixed(2)}% of them will both not truely have a COVID infection and be told they do have one (aka will be FPs).</p>
            </div>
         )} />

      </>

   )
}