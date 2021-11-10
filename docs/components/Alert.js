/* This example requires Tailwind CSS v2.0+ */
import { ExclamationIcon } from '@heroicons/react/solid'

export default function Example({ title, children }) {
   return (
      <div className={`relative ${title ? 'mt-10' : ''}`}>
         {title && <div className="inline-block bg-nhsuk-yellow text-nhsuk-text p-8 py-3 text-xl font-semibold">{title}</div>}
         <div className={`p-8 text-lg text-nhsuk-text bg-nhsuk-pale-yellow border border-nhsuk-yellow ${title ? 'pt-10 -mt-6' : ''}`}>
            {children}
         </div>
      </div>
   )
}
