import { Disclosure } from '@headlessui/react'
import Container from 'components/Container'
import Sidebar from 'components/layouts/parts/Sidebar'
import Footer from './parts/Footer'
import Header from './parts/Header'
import Pagination from './parts/Pagination'

export default function PageLayout({ children, title, category, formatting, darkBackground, noPagination }) {
   return (
      <>

         {/* Page */}
         <div className="min-h-full">

            {/* Header */}
            <Header category={category} />

            {/* Main page */}
            <div className={`${darkBackground ? 'bg-gray-50' : ''}`}>
               <main className="flex-1">
                  <Container>
                     <div className="flex flex-col py-8 lg:flex-row lg:py-12">

                        {/* Sidebar */}
                        <Disclosure>
                           {({ open }) => (
                              <>
                                 {/* Desktop sidebar */}
                                 <div className="hidden lg:flex relative w-80 flex-shrink-0">
                                    <div className="-mt-6">
                                       <div className="sticky top-0 pt-6">
                                          <Sidebar />
                                       </div>
                                    </div>
                                 </div>

                                 {/* Mobile sidebar */}
                                 <div className="lg:hidden flex flex-col mb-8">

                                    {/* Mobile sidebar content */}
                                    <Disclosure.Panel className="mb-6">
                                       <Sidebar />
                                    </Disclosure.Panel>

                                    {/* Mobile sidebar toggle */}
                                    <Disclosure.Button className="bg-gray-100 flex justify-center items-center p-4 text-gray-500 underline">
                                       {open ? 'Close menu' : 'Show menu'}
                                    </Disclosure.Button>

                                 </div>
                              </>
                           )}
                        </Disclosure>

                        {/* Main panel */}
                        <div className="flex-1 space-y-10">

                           {/* Content */}
                           <div className={`${formatting ? 'prose max-w-none' : ''}`}>
                              {children}
                           </div>

                           {/* Pagination */}
                           {!noPagination && <Pagination />}

                        </div>

                     </div>
                  </Container>
               </main>
            </div>
         </div>

         {/* Footer */}
         <Footer />

      </>
   )
}