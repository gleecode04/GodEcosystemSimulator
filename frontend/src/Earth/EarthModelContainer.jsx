import { Canvas } from "@react-three/fiber";
import { EarthModel } from "./EarthModel";
import { OrbitControls } from "@react-three/drei";
import { Suspense } from "react";
import "./EarthModelContainer.css";

const EarthModelContainer = () => {
    return (
        <div className="canvas-container">
            <Canvas>
                <Suspense fallback="loading...">
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <EarthModel />
                    <OrbitControls 
                        enableZoom={false}
                        enablePan={false}
                        autoRotate
                        autoRotateSpeed={0.5}
                        minPolarAngle={Math.PI / 2.5}
                        maxPolarAngle={Math.PI / 1.5}
                    />
                </Suspense>
            </Canvas>
        </div>
    );
};

export default EarthModelContainer;