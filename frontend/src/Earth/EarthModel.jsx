import React from 'react'
import { useGLTF } from '@react-three/drei'

export function EarthModel(props) {
  const { nodes, materials } = useGLTF('/earthModel.glb')
  return (
    <group {...props} dispose={null}>
      <mesh geometry={nodes.earth4_blinn1_0.geometry} material={materials.blinn1} />
      <mesh geometry={nodes.earth4_lambert1_0.geometry} material={materials.lambert1} />
    </group>
  )
}

useGLTF.preload('/earth.glb')