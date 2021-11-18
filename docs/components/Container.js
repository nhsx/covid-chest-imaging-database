export default function Container ({ children, fullwidth }) {
   return (
      <div className={`mx-auto px-4 sm:px-6 lg:px-8 ${fullwidth ? '' : 'max-w-6xl'}`}>
         {children}
      </div>
   )
}