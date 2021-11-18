import Link from 'next/link'
import { useRouter } from 'next/router'
import { Disclosure } from '@headlessui/react'
import { MenuIcon, XIcon } from '@heroicons/react/outline'
import { SearchIcon } from '@heroicons/react/solid'
import { prefix } from 'lib/prefix'
import { mainNavigation } from 'lib/menus'
import Container from 'components/Container'

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
                        item.name === category ? 'md:border-b-4 md:pb-3 border-white font-semibold' : 'border-transparent',
                        'group flex items-center px-4 py-4 border-l-4 md:border-l-0 text-white hover:underline text-base focus:bg-nhsuk-yellow focus:text-black focus:border-black md:focus:border-b-4 md:focus:pb-3'
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

export default function Header({ category, fullwidth }) {
   return (
      <Disclosure as="nav" className="bg-blue-500">
         {({ open }) => (
            <>

               {/* Nav */}
               <Container fullwidth={fullwidth}>

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
}
