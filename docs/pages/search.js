import Link from 'next/link'
import Introduction from 'components/Introduction'
import PageLayout from 'components/layouts/PageLayout'

const posts = require('cache/post-data').posts

const Search = ({ results }) => {
   return (
      <PageLayout noPagination>
         <Introduction title="Search Results" description={results ? `Your search returned ${results.length} results` : 'No results found'} />
         {
            results && (
               <div className="space-y-6">
                  {results.map(result => (
                     <Link key={result.slug} href={`/${result.slug}`}>
                        <a className="block">
                           <h3 className="text-lg font-medium text-nhsuk-text mb-1">{result.title}</h3>
                           <p className="text-nhsuk-secondary-text">{result.summary}</p>
                        </a>
                     </Link>
                  ))}
               </div>
            )
         }
      </PageLayout>
   )
}

export async function getServerSideProps(context) {
   const { q } = context.query
   if (q) {
      const results = posts.filter(
         post => {
            return (
               post
                  .title
                  .toLowerCase()
                  .includes(q.toLowerCase()) ||
               post
                  .content
                  .toLowerCase()
                  .includes(q.toLowerCase())
            );
         }
      );
      return {
         props: {
            results
         }
      }
   }

   // By default, return nothing 
   return {
      props: {},
   }

}

export default Search
