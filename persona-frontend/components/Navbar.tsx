'use client'
import React from 'react'
import {motion} from 'framer-motion'

function Navbar() {
  return (
    <nav className='sticky top-0'>
        <div className=' pl-10 '>
            <motion.h1 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className='text-3xl font-bold mask-b-from-50% mask-b-to-90% text-brown-800 text-shadow-sm text-shadow-golden-400 '>Persona</motion.h1>
        </div>
    </nav>
  )
}

export default Navbar