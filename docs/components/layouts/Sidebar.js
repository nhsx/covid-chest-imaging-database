import Link from 'next/link'
import { useRouter } from 'next/dist/client/router'
import { otherNavigation, techNavigation } from 'lib/menus'
import { BookOpenIcon, CogIcon } from '@heroicons/react/solid'

// Hepler function
function classNames(...classes) {
   return classes.filter(Boolean).join(' ')
}

// Menu heading
const MenuHeading = (props) => (
   <div className="flex items-center space-x-3">
      {props.icon && (
         <div>
            <div className="bg-blue-500 rounded p-1">
               <props.icon className="w-4 h-4 text-white" />
            </div>
         </div>
      )}
      <div>
         <p className="font-semibold text-gray-400 uppercase tracking-wider text-xs">
            {props.children}
         </p>
      </div>
   </div>
)

// Individual menu item 
const Menu = ({ navigation }) => {
   const router = useRouter()
   const { slug } = router.query
   return (
      <nav className="mb-4 space-y-1 border-l border-gray-200 ml-3">
         {navigation.map((item) => (
            <Link
               key={item.name}
               href={item.href}
            >
               <a
                  className={classNames(
                     item.href === `/${slug}` ? 'underline font-medium -ml-1 pl-7 text-blue-500' : 'text-gray-500',
                     'relative group flex items-center py-2 px-6 text-base'
                  )}
               >
                  {item.href === `/${slug}` && (
                     <div className="flex absolute -left-1 top-1/2 -mt-2 rounded-full border w-4 h-4 bg-white p-px">
                        <div className="rounded-full bg-blue-500 flex-1"></div>
                     </div>
                  )}
                  {item.name}
               </a>
            </Link>
         ))}
      </nav>
   )
}

export default function Sidebar() {
   return (
      <>
         <div className="flex-grow flex flex-col space-y-8">
            <div className="space-y-4">
               <MenuHeading icon={CogIcon}>Technical Documentation</MenuHeading>
               <Menu navigation={techNavigation} />
            </div>
            <div className="space-y-4">
               <MenuHeading icon={BookOpenIcon}>Other Information</MenuHeading>
               <Menu navigation={otherNavigation} />
            </div>
         </div>
      </>
   )
}