import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/solid';
import { useEffect, useMemo, useState } from 'react';

import Card from 'components/Card';
import ROCLine from 'components/charts/ROCLine';
import NegativeBar from 'components/charts/NegativeBar';
import PositiveBar from 'components/charts/PositiveBar';

import { parseFile } from 'lib/csv';

const StatOutput = ({ title, value }) => (
   <Card>
      <div className="px-6 py-4">
         <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
         <dd className="text-lg font-semibold text-gray-900">{parseFloat(value).toFixed(2)}%</dd>
      </div>
   </Card>
)

const GlossaryRow = ({ title, description }) => (
   <div className="grid sm:grid-cols-12 gap-2 text-nhsuk-text">
      <dt className="sm:col-span-3 font-medium">{title}</dt>
      <dd className="sm:col-span-9">{description}</dd>
   </div>
)

export default function OperatingPointCharts() {

   // Local state
   const [percentage, setPercentage] = useState(5)
   const [operatingPoint, setOperatingPoint] = useState(0.4)
   const [rocData, setRocData] = useState(null)

   // Calculate nearest operating point 
   const nearestOperatingPoint = useMemo(() => rocData && rocData.find(point => parseFloat(point.operatingPoint).toFixed(2) - operatingPoint < 0.02), [rocData, operatingPoint])

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
      <div className="space-y-4">

         {/* Controls */}
         <Card withPadding>
            <div>
               <div className="grid grid-cols-2 gap-6">
                  <div>
                     <div className="flex justify-between items-center mb-2 ">
                        <div>
                           <label className="font-medium">Operating point</label>
                        </div>
                        <div>
                           <span className="text-sm text-gray-500">{operatingPoint}</span>
                        </div>
                     </div>
                     <input type="range" min="0" max="1" step="0.01" className="w-full bg-nhsuk-blue" value={operatingPoint} onChange={(e) => setOperatingPoint(e.target.value)} />
                  </div>
                  <div>
                     <div className="flex justify-between items-center mb-2 ">
                        <div>
                           <label className="font-medium">Prevalence (% of population with COVID):</label>
                        </div>
                        <div>
                           <span className="text-sm text-gray-500">{percentage}%</span>
                        </div>
                     </div>
                     <input type="range" min="0" max="100" step="1" className="w-full" value={percentage} onChange={(e) => setPercentage(e.target.value)} />
                  </div>
               </div>
            </div>
         </Card>

         {/* Middle */}
         <div className="grid grid-cols-12 gap-4">

            {/* Context */}
            <div className="col-span-4 space-y-4 md:relative">
               <div className="md:sticky md:top-0 md:-mt-4">

                  {/* Outputs */}
                  <div className="space-y-4 md:pt-4">
                     <div className="grid gap-4 sm:grid-cols-1">
                        <StatOutput title="Sensitivity" value={sensitivity * 100} />
                        <StatOutput title="Specificity" value={specificity * 100} />
                        <StatOutput title="Raw Accuracy" value={accuracy} />
                     </div>
                     <div className="grid gap-4 sm:grid-cols-2">
                        <StatOutput title="PPV" value={ppv * 100} />
                        <StatOutput title="NPV" value={npv * 100} />
                        <StatOutput title="TP" value={tp_final} />
                        <StatOutput title="TN" value={tn_final} />
                        <StatOutput title="FP" value={fp_final} />
                        <StatOutput title="FN" value={fn_final} />
                     </div>
                  </div>

               </div>
            </div>

            {/* Charts */}
            <div className="col-span-8 space-y-4">

               {/* FOC */}
               <Card withPadding>
                  <ROCLine height={200} plotData={rocData} fp={fp} tp={tp} />
               </Card>

               {/* Positive bar */}
               <Card withPadding>
                  <PositiveBar height={200} percentage={percentage} correct={tp_final} incorrect={fn_final} />
               </Card>

               {/* Negative bar */}
               <Card withPadding>
                  <NegativeBar height={200} percentage={percentage} correct={tn_final} incorrect={fp_final} />
               </Card>

            </div>

         </div>

         {/* Breakdown */}
         <Card withPadding>
            <div className="text-nhsuk-text text-sm">
               <h3 className="text-nhsuk-text text-base font-medium mb-2">Within all people the model tests...</h3>
               <p>{(tp_final + fp_final).toFixed(2)}% of them will be predicted to have a COVID infection (aka TPs + FPs).</p>
               <p>{(fn_final).toFixed(2)}% of them will both truely have a COVID infection and be told they do not have one (aka will be FNs).</p>
               <p>{(fp_final).toFixed(2)}% of them will both not truely have a COVID infection and be told they do have one (aka will be FPs).</p>
            </div>
         </Card>

         {/* Glossary */}
         <Card>
            <Disclosure>
               {({ open }) => (
                  <>
                     <Disclosure.Button className="p-6 w-full flex space-x-4 justify-between text-nhsuk-text">
                        <div className="text-base font-medium">
                           Glossary
                        </div>
                        <div>
                           {
                              open ? <ChevronUpIcon className="w-6 h-6" /> : <ChevronDownIcon className="w-6 h-6" />
                           }
                        </div>
                     </Disclosure.Button>
                     <Disclosure.Panel className="p-6 pt-3">
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
                     </Disclosure.Panel>
                  </>
               )}
            </Disclosure>
         </Card>

      </div>
   )
}