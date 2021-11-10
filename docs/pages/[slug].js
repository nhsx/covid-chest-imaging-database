import fs from 'fs'
import path from 'path'
import { serialize } from 'next-mdx-remote/serialize'
import { MDXRemote } from 'next-mdx-remote'
import PageLayout from 'components/layouts/PageLayout';
import MDXComponents from 'components/documentation/MDXComponents';
import matter from 'gray-matter';

function Post({ source, meta }) {
   return (
      <PageLayout {...meta} formatting={meta.formatting ?? true} darkBackground={meta.offwhite}>
         <MDXRemote {...source} components={MDXComponents} />
      </PageLayout>
   )
}

export async function getStaticPaths() {
   const filenames = fs.readdirSync('documentation')
   const slugs = filenames.map(filename => filename.replace(/\.mdx$/, ''))
   return {
      paths: slugs.map((slug) => ({ params: { slug } })),
      fallback: false
   };
}

export async function getStaticProps({ params }) {
   const fullPath = path.join('documentation', `${params.slug}.mdx`)
   const fileContents = fs.readFileSync(fullPath, 'utf8')
   const { content, data } = matter(fileContents)
   const mdxSource = await serialize(content, { scope: data })
   return { props: { source: mdxSource, meta: data } }
}

export default Post