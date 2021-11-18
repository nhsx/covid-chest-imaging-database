import { useRouter } from 'next/router'
import { otherNavigation, techNavigation } from 'lib/menus'
import Button from 'components/Button'

export default function Pagination() {

   // Access router 
   const router = useRouter()
   const { slug } = router.query

   // Merge navigations 
   const navigation = [...techNavigation, ...otherNavigation]

   // Get current nav item 
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