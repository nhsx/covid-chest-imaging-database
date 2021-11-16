import Link from "next/link"

export default function Button({ color, children, href, type, onClick = () => {} }) {

   const baseClass = "inline-flex items-center px-4 py-3 text-lg duration-100 font-semibold rounded shadow-nhsuk-button focus:bg-nhsuk-focus focus:text-nhsuk-text active:shadow-none"

   let colorClass
   switch(color) {
      default: 
      case "primary":
         colorClass = 'bg-green-500 text-white hover:bg-green-600'
         break 
      case "secondary":
         colorClass = 'bg-gray-500 text-white hover:bg-gray-600'
         break 
      case "white":
         colorClass = 'bg-white text-nhsuk-text'
         break  
   }

   const finalClass = `${baseClass} ${colorClass}`
   
   return href ? (
      <Link href={href}>
         <a className={finalClass}>
            {children}
         </a>
      </Link>
   ) : (
      <button type={type || 'button'} className={finalClass} onClick={onClick}>
         {children}
      </button>
   )
}