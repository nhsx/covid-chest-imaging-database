export default function Card({ children, withPadding }) {
   return (
      <div className={`bg-white ${withPadding ? 'p-6' : ''}`}>
         {children}
      </div>
   )
}