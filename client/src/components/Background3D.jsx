import { useEffect, useRef, useState } from 'react';
import NET from 'vanta/dist/vanta.net.min';
import * as THREE from 'three';

const Background3D = ({ children }) => {
    const [vantaEffect, setVantaEffect] = useState(null);
    const vantaRef = useRef(null);

    useEffect(() => {
        const initVanta = () => {
            if (!vantaEffect && vantaRef.current) {
                try {
                    setVantaEffect(
                        NET({
                            el: vantaRef.current,
                            THREE: THREE,
                            mouseControls: true,
                            touchControls: true,
                            gyroControls: false,
                            minHeight: 200.00,
                            minWidth: 200.00,
                            scale: 1.00,
                            scaleMobile: 1.00,
                            color: 0x3f51b5,
                            backgroundColor: 0x0f172a,
                            points: 12.00,
                            maxDistance: 22.00,
                            spacing: 18.00
                        })
                    );
                } catch (error) {
                    console.error("[Vanta] Failed to initialize:", error);
                }
            }
        };

        initVanta();

        return () => {
            if (vantaEffect) vantaEffect.destroy();
        };
    }, [vantaEffect]);

    return (
        <div ref={vantaRef} style={{ minHeight: '100vh', width: '100%', position: 'relative' }}>
            <div style={{ position: 'relative', zIndex: 1 }}>
                {children}
            </div>
        </div>
    );
};

export default Background3D;
