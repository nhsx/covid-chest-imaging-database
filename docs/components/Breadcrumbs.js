import Link from 'next/link'
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/solid'

export default function Breadcrumbs({ pages }) {
   return (
      <nav className="bg-white flex" aria-label="Breadcrumb">
         <ol role="list" className="max-w-5xl w-full mx-auto px-4 flex space-x-4 sm:px-6 lg:px-8">
            <li className="flex">
               <div className="flex items-center">
                  <Link href="/">
                     <a className="text-sm font-medium text-blue-500 hover:text-blue-600">
                        Overview
                     </a>
                  </Link>
               </div>
            </li>
            {pages.map((page, index) => (
               <li key={page.title} className="flex flex-shrink-0 py-4">
                  <div className="flex items-center">
                     <ChevronRightIcon className="w-4 h-4 text-gray-300" />
                     <a
                        href={page.href}
                        className="ml-4 font-medium text-sm text-blue-500 hover:text-blue-600"
                        aria-current={(index === pages.length - 1) ? 'page' : undefined}
                     >
                        {page.title}
                     </a>
                  </div>
               </li>
            ))}
         </ol>
      </nav>
   )
}
