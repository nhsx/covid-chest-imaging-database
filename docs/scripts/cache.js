const fs = require('fs')
const path = require('path')
const matter = require('gray-matter')

function postData() {
   const postsDirectory = path.join(process.cwd(), 'documentation')
   const fileNames = fs.readdirSync(postsDirectory)
   const posts = fileNames.map(fileName => {
      const slug = fileName.replace(/\.mdx$/, '')
      const fullPath = path.join(postsDirectory, fileName)
      const fileContents = fs.readFileSync(fullPath, 'utf8')
      const matterResult = matter(fileContents)
      return {
         slug,
         content: matterResult.content,
         ...matterResult.data
      }
   })
   return `export const posts = ${JSON.stringify(posts)}`
}

try {
   fs.readdirSync('cache')
} catch (e) {
   fs.mkdirSync('cache')
}

fs.writeFile('cache/post-data.js', postData(), function (err) {
   if (err) return console.log(err);
   console.log('Posts cached.');
})