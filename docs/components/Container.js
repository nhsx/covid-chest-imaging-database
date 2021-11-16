export default function Container ({ children }) {
   return (
      <div className={`mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl`}>
         {children}
      </div>
   )
}