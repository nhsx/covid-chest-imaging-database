export default function Introduction({ title, description }) {
   return (
      <div className="mb-10">
         {title && <h1 className="text-2xl md:text-4xl text-gray-800 font-bold mb-6">{title}</h1>}
         {description && (
            <p className="text-lg md:text-xl text-nhsuk-secondary-text">
               {description}
            </p>
         )}
      </div>
   )
}