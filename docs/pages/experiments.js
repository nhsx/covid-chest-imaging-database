import ModelFairness from 'components/charts/ModelFairness'
import OperatingPoint from 'components/charts/OperatingPoint'
import Footer from 'components/layouts/parts/Footer'
import Header from 'components/layouts/parts/Header'
import { useState } from 'react'

const Container = ({ children }) => {
   return (
      <div className={`px-4 sm:px-6 lg:px-8 flex-1`}>
         {children}
      </div>
   )
}

const StatsMenuItem = ({ title, active, onClick }) => {
   return (
      <button type="button" onClick={onClick} className={`${active ? 'bg-white text-nhsuk-text' : 'text-white hover:bg-blue-600'} px-3 py-2 sm:px-5 sm:py-3 font-medium focus:bg-nhsuk-focus focus:text-nhsuk-text flex-shrink-0`}>
         {title}
      </button>
   )
}

const StatsMenu = ({ currentNavItem, setCurrentNavItem }) => {
   return (
      <nav className="flex p-2 space-x-2 items-center bg-blue-700">
         {navigation.map(nav => <StatsMenuItem key={nav.title} title={nav.title} active={currentNavItem.title === nav.title} onClick={() => setCurrentNavItem(nav)} />)}
      </nav>
   )
}

// Define navigation 
const navigation = [
   { title: 'Operating point', component: <OperatingPoint /> },
   { title: 'Model fairness', component: <ModelFairness /> },
]

export default function Experiments({ category, children }) {

   // Local state 
   const [currentNavItem, setCurrentNavItem] = useState(navigation[0])

   return (
      <div className="flex flex-col min-h-screen">

         {/* Header */}
         <Header category="Experiments" />

         {/* Main content */}
         <main className="flex-1 flex items-stretch py-8 sm:py-12 bg-gray-50">
            {currentNavItem.component}
         </main>

         {/* Footer */}
         <Footer />

      </div>
   )
}