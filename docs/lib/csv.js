import Papa from 'papaparse'
import { prefix } from './prefix'

export const loadFile = async (path) => {
   if (!path) return false
   const response = await fetch(`${prefix}${path}`)
   const reader = response.body.getReader()
   const decoder = new TextDecoder('utf-8')
   const encoded = await reader.read()
   const decoded = decoder.decode(encoded.value)
   return decoded
}

export const parseFile = async (path) => {
   const data = await loadFile(path)
   return new Promise(resolve => {
      Papa.parse(data, {
         skipEmptyLines: true,
         complete: (results) => {
            resolve(results.data)
         },
         error: err => {
            reject(err)
         }
      });
   });
}