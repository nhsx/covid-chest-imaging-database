import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import Button from './Button'

export default function Modal({ show, onClose, title, content }) {
   return (
      <>
         <Transition appear show={show} as={Fragment}>
            <Dialog
               as="div"
               className="fixed inset-0 z-10 overflow-y-auto"
               onClose={onClose}
            >
               <div className="min-h-screen px-4 text-center">
                  <Transition.Child
                     as={Fragment}
                     enter="ease-out duration-300"
                     enterFrom="opacity-0"
                     enterTo="opacity-100"
                     leave="ease-in duration-200"
                     leaveFrom="opacity-100"
                     leaveTo="opacity-0"
                  >
                     <Dialog.Overlay className="fixed inset-0 bg-blue-800 bg-opacity-80" />
                  </Transition.Child>

                  {/* This element is to trick the browser into centering the modal contents. */}
                  <span
                     className="inline-block h-screen align-middle"
                     aria-hidden="true"
                  >
                     &#8203;
                  </span>
                  <Transition.Child
                     as={Fragment}
                     enter="ease-out duration-300"
                     enterFrom="opacity-0 scale-95"
                     enterTo="opacity-100 scale-100"
                     leave="ease-in duration-200"
                     leaveFrom="opacity-100 scale-100"
                     leaveTo="opacity-0 scale-95"
                  >
                     <div className="inline-block w-full max-w-4xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl md:p-8">
                        <Dialog.Title
                           as="h3"
                           className="text-xl font-semibold leading-6 text-gray-900"
                        >
                           {title}
                        </Dialog.Title>
                        
                        <div className="mt-4 max-h-96 overflow-y-auto">
                           {content}
                        </div>

                        <div className="flex mt-6">
                           <Button onClick={onClose}>
                              Okay
                           </Button>
                        </div>
                     </div>
                  </Transition.Child>
               </div>
            </Dialog>
         </Transition>
      </>
   )
}
