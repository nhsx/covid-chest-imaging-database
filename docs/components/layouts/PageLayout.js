import Link from 'next/link'
import { useRouter } from 'next/router'
import { Disclosure } from '@headlessui/react'
import { MenuIcon, XIcon } from '@heroicons/react/outline'
import { SearchIcon } from '@heroicons/react/solid'
import { prefix } from '../../lib/prefix'
import { footerNavigation, mainNavigation, otherNavigation, techNavigation } from 'lib/menus'
import Container from 'components/Container'
import Sidebar from 'components/layouts/Sidebar'
import Button from 'components/Button'

// Hepler function
function classNames(...classes) {
   return classes.filter(Boolean).join(' ')
}

// Main menu
const Menu = ({ category }) => {
   return (
      <div className="border-t border-white border-opacity-20">
         <nav className="flex flex-col space-y-2 md:space-y-0 md:flex-row md:space-x-6">
            {mainNavigation.map((item) => (
               <Link
                  key={item.name}
                  href={item.href}
               >
                  <a
                     className={classNames(
                        item.name === category ? 'border-white font-semibold' : 'border-transparent',
                        'group flex items-center px-4 py-3 border-l-4 md:border-l-0 md:border-b-4 text-white hover:underline text-base focus:bg-nhsuk-yellow focus:text-black focus:border-black'
                     )}
                  >
                     {item.name}
                  </a>
               </Link>
            ))}
         </nav>
      </div>
   )
}

// Logo 
const Logo = () => (
   <Link href="/">
      <a className="flex flex-col space-y-6 md:space-y-4 lg:space-y-0 lg:flex-row lg:items-center lg:space-x-2 flex-shrink-0 text-white">
         <span>
            <img
               className="h-10 w-auto"
               src={`${prefix}/logo-inverted.svg`}
               alt="NCCID"
            />
         </span>
         <span className="text-sm lg:text-lg">
            National COVID-19 Chest Image Database (NCCID)
         </span>
      </a>
   </Link>
)

// Search box
const SearchBox = () => {
   const router = useRouter()
   const { q } = router.query
   return (
      <div className="flex-1 flex items-center space-x-6">
         <form action={`${prefix}/search/`} method="GET" className="flex-1 justify-stretch relative flex">
            <div className="flex-1">
               <input type="text" name="q" placeholder="Search" className="w-full border-2 border-transparent focus:ring-nhsuk-focus focus:ring-4 rounded-tl rounded-bl sm:text-sm" defaultValue={q || ''} />
            </div>
            <div>
               <button type="submit" className="w-full h-full flex-1 bg-gray-50 rounded-tr rounded-br px-3 text-blue-500 focus:bg-nhsuk-yellow focus:text-black ">
                  <SearchIcon className="w-6 h-6" />
               </button>
            </div>
         </form>
         <Link href="https://github.com/nhsx/covid-chest-imaging-database">
            <a
               target="_BLANK"
               className="rounded-full"
            >
               <svg className="w-10 h-10 flex-shrink-0 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 17 16" fill="none">
                  <g clipPath="url(githublogo)">
                     <path fill="currentColor" fillRule="evenodd" d="M8.18391.249268C3.82241.249268.253906 3.81777.253906 8.17927c0 3.46933 2.279874 6.44313 5.451874 7.53353.3965.0991.49563-.1983.49563-.3965v-1.3878c-2.18075.4956-2.67638-.9912-2.67638-.9912-.3965-.8922-.89212-1.1895-.89212-1.1895-.69388-.4957.09912-.4957.09912-.4957.793.0992 1.1895.793 1.1895.793.69388 1.2887 1.88338.8922 2.27988.6939.09912-.4956.29737-.8921.49562-1.0904-1.78425-.1982-3.5685-.8921-3.5685-3.96496 0-.89212.29738-1.586.793-2.08162-.09912-.19825-.3965-.99125.09913-2.08163 0 0 .69387-.19825 2.18075.793.59475-.19825 1.28862-.29737 1.9825-.29737.69387 0 1.38775.09912 1.98249.29737 1.4869-.99125 2.1808-.793 2.1808-.793.3965 1.09038.1982 1.88338.0991 2.08163.4956.59475.793 1.28862.793 2.08162 0 3.07286-1.8834 3.66766-3.66764 3.86586.29737.3965.59474.8921.59474 1.586v2.1808c0 .1982.0991.4956.5948.3965 3.172-1.0904 5.4518-4.0642 5.4518-7.53353-.0991-4.3615-3.6676-7.930002-8.02909-7.930002z" clipRule="evenodd" className="jsx-1651122719"></path>
                  </g>
                  <defs>
                     <clipPath id="githublogo">
                        <path fill="transparent" d="M0 0h15.86v15.86H0z" transform="translate(.253906 .0493164)"></path>
                     </clipPath>
                  </defs>
               </svg>
            </a>
         </Link>
      </div>
   )
}

// Header
const Header = ({ category }) => (
   <Disclosure as="nav" className="bg-blue-500">
      {({ open }) => (
         <>

            {/* Nav */}
            <Container>

               {/* Top */}
               <div className="flex justify-between py-6">

                  {/* Logo */}
                  <div className="flex">
                     <Logo />
                  </div>

                  {/* Searchbox  */}
                  <div className="hidden md:flex">
                     <SearchBox />
                  </div>

                  {/* Menu button */}
                  <div className="-mr-2 flex items-start md:hidden">
                     {/* Mobile menu button */}
                     <Disclosure.Button className="bg-white inline-flex items-center justify-center p-2 text-nhsuk-text hover:bg-gray-100 focus:bg-nhsuk-yellow focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-nhsuk-yellow">
                        <span className="sr-only">Open main menu</span>
                        {open ? (
                           <XIcon className="block h-6 w-6" aria-hidden="true" />
                        ) : (
                           <MenuIcon className="block h-6 w-6" aria-hidden="true" />
                        )}
                     </Disclosure.Button>
                  </div>

               </div>

               {/* Desktop menu */}
               <div className="hidden md:block">
                  <Menu category={category} />
               </div>

            </Container>

            {/* Mobile dropdown */}
            <Disclosure.Panel className="md:hidden">
               <Menu category={category} />
               <div className="flex p-4 border-r border-white border-opacity-20">
                  <SearchBox />
               </div>
            </Disclosure.Panel>

         </>
      )}
   </Disclosure>
)

// Footer 
const Footer = () => (
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

// Pagination 
const Pagination = () => {

   const router = useRouter()
   const { slug } = router.query
   const navigation = [...techNavigation, ...otherNavigation]
   const currentNavItemIndex = navigation.findIndex(item => item.href === `/${slug}`)

   return (
      <div className="flex justify-between items-center">
         <div>
            {currentNavItemIndex > 0 && (
               <Button href={navigation[currentNavItemIndex - 1].href}>
                  Previous
               </Button>
            )}
         </div>
         <div>
            {(currentNavItemIndex < navigation.length - 1) && (
               <Button href={navigation[currentNavItemIndex + 1].href}>
                  Next
               </Button>
            )}
         </div>
      </div>
   )
}

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