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

// const Header = ({ currentNavItem, setCurrentNavItem }) => {
//    return (
//       <>
//          {/* Header */}
//          <header className="py-6 sticky top-0  backdrop-blur-lg z-10">
//             <Container>
//                <div className="flex space-x-6 justify-between items-center">

//                   {/* Title */}
//                   <div className="xl:flex-1 flex justify-start">
//                      <div>
//                         <Link href="/">
//                            <a className="text-white flex items-center">
//                               <ArrowLeftIcon className="w-4 h-4 hidden sm:inline-block sm:mr-2" />
//                               <span className="underline">Back to website</span>
//                            </a>
//                         </Link>
//                         <h1 className="text-white text-xl sm:text-2xl font-bold mt-1">NCCID Statistics</h1>
//                      </div>
//                   </div>

//                   {/* Nav */}
//                   <div className="hidden flex-1 lg:flex justify-center">
//                      <Menu currentNavItem={currentNavItem} setCurrentNavItem={setCurrentNavItem} />
//                   </div>

//                   {/* Logo */}
//                   <div className="xl:flex-1 flex justify-end">
//                      <Link href="/">
//                         <a>
//                            <img src="/logo-inverted.svg" alt="NHS UK" className="h-8 sm:h-12" />
//                         </a>
//                      </Link>
//                   </div>

//                </div>
//             </Container>
//          </header>

//          {/* Mobile menu */}
//          <div className="flex justify-center lg:hidden py-3 mb-3">
//             <Menu currentNavItem={currentNavItem} setCurrentNavItem={setCurrentNavItem} />
//          </div>
//       </>
//    )
// }

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