const withMDX = require('@next/mdx')({
   extension: /\.mdx$/
})
module.exports = withMDX({
   basePath: process.env.NEXT_PUBLIC_BASE_PATH,
   assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH,
   pageExtensions: ['js', 'jsx', 'mdx'],
   trailingSlash: process.env.NEXT_PUBLIC_TRAILING_SLASH || false
})