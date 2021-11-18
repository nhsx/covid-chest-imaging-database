import fs from 'fs'
import path from 'path'
import { serialize } from 'next-mdx-remote/serialize'
import { MDXRemote } from 'next-mdx-remote'
import PageLayout from 'components/layouts/PageLayout';
import MDXComponents from 'components/documentation/MDXComponents';
import matter from 'gray-matter';

function Home({ source, meta }) {
   return (
      <PageLayout {...meta} formatting={meta.formatting ?? true} darkBackground={meta.offwhite}>
         <MDXRemote {...source} components={MDXComponents} />
      </PageLayout>
   )
}

export async function getStaticProps({ params }) {
   const fullPath = path.join('documentation', `home.mdx`)
   const fileContents = fs.readFileSync(fullPath, 'utf8')
   const { content, data } = matter(fileContents)
   const mdxSource = await serialize(content, { scope: data })
   return { props: { source: mdxSource, meta: data } }
}

export default Home