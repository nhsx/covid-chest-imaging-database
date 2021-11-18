import Link from 'next/link'
import { footerNavigation } from 'lib/menus'
import Container from 'components/Container'

export default function Footer() {
   return (
      <div className="bg-gray-200 text-gray-500 border-t-4 border-blue-500 py-8 md:py-10">
         <Container>
            <div className="space-y-10 sm:space-y-6">
               <div className="flex flex-col space-y-6 md:space-y-0 md:space-x-10 md:flex-row md:justify-between md:items-start">
                  <div className="space-y-2 md:space-y-0 -ml-4">
                     {footerNavigation.map(item => (
                        <Link key={item.name} href={item.href}>
                           <a className="block md:inline-block underline px-4 pb-4">{item.name}</a>
                        </Link>
                     ))}
                  </div>
                  <div className="flex-shrink-0">
                     © Copyright 2020 NHSX
                  </div>
               </div>
               <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-3 text-base">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 483.2 195.7" height="17" width="41" focusable="false">
                     <path fill="currentColor" d="M421.5 142.8V.1l-50.7 32.3v161.1h112.4v-50.7zm-122.3-9.6A47.12 47.12 0 0 1 221 97.8c0-26 21.1-47.1 47.1-47.1 16.7 0 31.4 8.7 39.7 21.8l42.7-27.2A97.63 97.63 0 0 0 268.1 0c-36.5 0-68.3 20.1-85.1 49.7A98 98 0 0 0 97.8 0C43.9 0 0 43.9 0 97.8s43.9 97.8 97.8 97.8c36.5 0 68.3-20.1 85.1-49.7a97.76 97.76 0 0 0 149.6 25.4l19.4 22.2h3v-87.8h-80l24.3 27.5zM97.8 145c-26 0-47.1-21.1-47.1-47.1s21.1-47.1 47.1-47.1 47.2 21 47.2 47S123.8 145 97.8 145"></path>
                  </svg>
                  <span className="">
                     All content is available under the Open Government Licence v3.0, except where otherwise stated.
                  </span>
               </div>
            </div>
         </Container>
      </div>
   )
}