/**
 * ============================================================================
 * 3D CYBER-FORENSIC COMMAND CENTER ENGINE
 * Powered by Three.js (r128) & WebGL
 * Optimizing Digital Forensic Security Via Secure Storage
 * ============================================================================
 */

(function () {
    'use strict';

    // --- GLOBAL 3D STATE ---
    const Forensic3D = {
        scene: null,
        camera: null,
        renderer: null,
        controls: null,
        clock: new THREE.Clock(),
        raycaster: new THREE.Raycaster(),
        mouse: new THREE.Vector2(-999, -999),
        
        // Interactive object registries
        evidenceNodes: [],
        blockchainBlocks: [],
        interactiveObjects: [],
        hoveredObject: null,
        selectedEvidence: null,
        
        // Animated components
        rotators: [],
        dataParticles: null,
        pipelineStream: null,
        tamperLight: null,
        quarantineMesh: null,
        severedLine: null,
        restorativeWave: null,
        
        // State variables
        currentStation: 'vault',
        isTampered: false,
        isCinematic: false,
        cinematicTimer: null,
        audioEnabled: false,
        audioCtx: null,
        ambientOsc: null,
        ambientGain: null,
        
        // Camera presets for stations
        stations: {
            vault: {
                camPos: new THREE.Vector3(0, 10, 26),
                target: new THREE.Vector3(0, 0, 0)
            },
            blockchain: {
                camPos: new THREE.Vector3(65, 14, -15),
                target: new THREE.Vector3(65, 0, -42)
            },
            ingest: {
                camPos: new THREE.Vector3(-65, 14, -15),
                target: new THREE.Vector3(-65, 0, -42)
            },
            tamper: {
                camPos: new THREE.Vector3(0, 14, 88),
                target: new THREE.Vector3(0, 0, 60)
            },
            storage: {
                camPos: new THREE.Vector3(0, 48, -45),
                target: new THREE.Vector3(0, 32, -72)
            }
        }
    };

    // Export to window for HTML UI hooks
    window.Forensic3D = Forensic3D;

    // --- INITIALIZATION ENTRY POINT ---
    document.addEventListener('DOMContentLoaded', () => {
        initAudioPreference();
        init3DScene();
        buildCyberEnvironment();
        buildVaultCoreMatrix();
        buildBlockchainHighway();
        buildIngestionPipeline();
        buildTamperLabPlatform();
        buildStorageMatrixComparison();
        setupInteractionListeners();
        setupUIEventListeners();
        fetchLiveForensicData();
        
        // Render loop
        animate();
    });

    // =========================================================================
    // 1. PROCEDURAL WEB AUDIO SYNTHESIZER
    // =========================================================================
    function initAudioPreference() {
        const saved = localStorage.getItem('forensic_3d_audio');
        Forensic3D.audioEnabled = (saved === 'true');
        updateAudioButtonUI();
    }

    function ensureAudioContext() {
        if (!Forensic3D.audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                Forensic3D.audioCtx = new AudioContext();
            }
        }
        if (Forensic3D.audioCtx && Forensic3D.audioCtx.state === 'suspended') {
            Forensic3D.audioCtx.resume();
        }
    }

    function toggleAudio() {
        ensureAudioContext();
        Forensic3D.audioEnabled = !Forensic3D.audioEnabled;
        localStorage.setItem('forensic_3d_audio', Forensic3D.audioEnabled ? 'true' : 'false');
        updateAudioButtonUI();

        if (Forensic3D.audioEnabled) {
            startAmbientDrone();
            playLaserPing(880, 0.15);
        } else {
            stopAmbientDrone();
        }
    }
    window.toggle3DAudio = toggleAudio;

    function updateAudioButtonUI() {
        const btn = document.getElementById('btn-toggle-audio');
        if (btn) {
            btn.innerHTML = Forensic3D.audioEnabled ? '🔊 Audio: ON' : '🔇 Audio: MUTED';
            if (Forensic3D.audioEnabled) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    }

    function startAmbientDrone() {
        if (!Forensic3D.audioEnabled || !Forensic3D.audioCtx) return;
        try {
            stopAmbientDrone();
            const ctx = Forensic3D.audioCtx;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            const filter = ctx.createBiquadFilter();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(55, ctx.currentTime); // Low A hum

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(120, ctx.currentTime);

            gain.gain.setValueAtTime(0.001, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.04, ctx.currentTime + 3);

            osc.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            Forensic3D.ambientOsc = osc;
            Forensic3D.ambientGain = gain;
        } catch (e) {
            console.warn('Ambient audio could not start:', e);
        }
    }

    function stopAmbientDrone() {
        if (Forensic3D.ambientOsc) {
            try {
                Forensic3D.ambientOsc.stop();
                Forensic3D.ambientOsc.disconnect();
            } catch (e) {}
            Forensic3D.ambientOsc = null;
        }
    }

    function playLaserPing(freq = 600, duration = 0.1) {
        if (!Forensic3D.audioEnabled || !Forensic3D.audioCtx) return;
        try {
            const ctx = Forensic3D.audioCtx;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(freq * 0.4, ctx.currentTime + duration);

            gain.gain.setValueAtTime(0.06, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + duration);
        } catch (e) {}
    }

    function playTamperAlarmSound() {
        if (!Forensic3D.audioEnabled || !Forensic3D.audioCtx) return;
        try {
            const ctx = Forensic3D.audioCtx;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.setValueAtTime(880, ctx.currentTime + 0.15);
            osc.frequency.setValueAtTime(440, ctx.currentTime + 0.3);
            osc.frequency.setValueAtTime(880, ctx.currentTime + 0.45);

            gain.gain.setValueAtTime(0.12, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.6);
        } catch (e) {}
    }

    function playRepairChime() {
        if (!Forensic3D.audioEnabled || !Forensic3D.audioCtx) return;
        try {
            const ctx = Forensic3D.audioCtx;
            [523.25, 659.25, 783.99, 1046.50].forEach((f, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                const startT = ctx.currentTime + (i * 0.08);

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(f, startT);

                gain.gain.setValueAtTime(0.08, startT);
                gain.gain.exponentialRampToValueAtTime(0.0001, startT + 0.4);

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.start(startT);
                osc.stop(startT + 0.4);
            });
        } catch (e) {}
    }

    // =========================================================================
    // 2. THREE.JS SCENE, CAMERA & RENDERER SETUP
    // =========================================================================
    function init3DScene() {
        const container = document.getElementById('webgl-canvas-container');
        if (!container) return;

        // Scene
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x040711, 0.0065);
        Forensic3D.scene = scene;

        // Camera
        const width = window.innerWidth;
        const height = window.innerHeight;
        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1500);
        camera.position.copy(Forensic3D.stations.vault.camPos);
        camera.lookAt(Forensic3D.stations.vault.target);
        Forensic3D.camera = camera;

        // Renderer
        const renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: false,
            powerPreference: 'high-performance'
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.15;
        renderer.domElement.id = 'webgl-canvas';
        container.appendChild(renderer.domElement);
        Forensic3D.renderer = renderer;

        // Orbit Controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 250;
        controls.minDistance = 6;
        controls.maxPolarAngle = Math.PI / 2 + 0.05; // Stay mostly above grid
        controls.target.copy(Forensic3D.stations.vault.target);
        Forensic3D.controls = controls;

        // Lights
        const ambientLight = new THREE.AmbientLight(0x0c1e38, 1.2);
        scene.add(ambientLight);

        // Neon Cyan directional key light
        const dirLightCyan = new THREE.DirectionalLight(0x00f0ff, 1.6);
        dirLightCyan.position.set(30, 60, 30);
        scene.add(dirLightCyan);

        // Neon Emerald secondary fill light
        const dirLightEmerald = new THREE.DirectionalLight(0x00ff9d, 1.0);
        dirLightEmerald.position.set(-30, 40, -30);
        scene.add(dirLightEmerald);

        // Violet accent rim light
        const dirLightViolet = new THREE.DirectionalLight(0x8b5cf6, 0.8);
        dirLightViolet.position.set(0, -30, 40);
        scene.add(dirLightViolet);

        // Core Vault Point Light
        const coreLight = new THREE.PointLight(0x00f0ff, 2.5, 45, 1.5);
        coreLight.position.set(0, 0, 0);
        scene.add(coreLight);
        Forensic3D.coreLight = coreLight;

        // Tamper Emergency Alarm Red Light (starts off)
        const tamperLight = new THREE.PointLight(0xff0055, 0, 150, 1.2);
        tamperLight.position.set(0, 20, 60);
        scene.add(tamperLight);
        Forensic3D.tamperLight = tamperLight;

        // Resize handler
        window.addEventListener('resize', onWindowResize, false);
    }

    function onWindowResize() {
        if (!Forensic3D.camera || !Forensic3D.renderer) return;
        const width = window.innerWidth;
        const height = window.innerHeight;
        Forensic3D.camera.aspect = width / height;
        Forensic3D.camera.updateProjectionMatrix();
        Forensic3D.renderer.setSize(width, height);
    }

    // =========================================================================
    // 3. CYBER ENVIRONMENT: GRID, STARS & VOLUMETRIC PARTICLES
    // =========================================================================
    function buildCyberEnvironment() {
        const scene = Forensic3D.scene;

        // Cyber Grid Floor (Custom Dual Ring Grid)
        const gridHelper = new THREE.GridHelper(300, 75, 0x00f0ff, 0x0a223f);
        gridHelper.position.y = -8;
        gridHelper.material.opacity = 0.4;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);

        // Concentric Hologram Radar Rings on floor
        const ringGeo = new THREE.RingGeometry(15, 15.4, 64);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.35
        });
        const floorRing1 = new THREE.Mesh(ringGeo, ringMat);
        floorRing1.rotation.x = Math.PI / 2;
        floorRing1.position.y = -7.9;
        scene.add(floorRing1);

        const ringGeo2 = new THREE.RingGeometry(45, 45.6, 96);
        const floorRing2 = new THREE.Mesh(ringGeo2, ringMat.clone());
        floorRing2.material.color.setHex(0x00ff9d);
        floorRing2.material.opacity = 0.25;
        floorRing2.rotation.x = Math.PI / 2;
        floorRing2.position.y = -7.9;
        scene.add(floorRing2);

        // Volumetric Cyber Particle Cloud (Starfield Dust)
        const particleCount = 2000;
        const pGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);

        const colorPalette = [
            new THREE.Color(0x00f0ff), // Cyan
            new THREE.Color(0x00ff9d), // Emerald
            new THREE.Color(0x8b5cf6), // Violet
            new THREE.Color(0xffb703)  // Amber
        ];

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 400;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 200 + 30;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 400;

            const c = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors[i * 3] = c.r;
            colors[i * 3 + 1] = c.g;
            colors[i * 3 + 2] = c.b;
        }

        pGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        pGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const pMaterial = new THREE.PointsMaterial({
            size: 1.4,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });

        const particleSystem = new THREE.Points(pGeometry, pMaterial);
        scene.add(particleSystem);
        Forensic3D.dataParticles = particleSystem;
    }

    // =========================================================================
    // 4. STATION 1: THE CRYPTOGRAPHIC VAULT CORE MATRIX
    // =========================================================================
    function buildVaultCoreMatrix() {
        const scene = Forensic3D.scene;
        const vaultGroup = new THREE.Group();
        vaultGroup.position.set(0, 0, 0);

        // 1. Central AES-256-GCM Faceted Diamond Core
        const coreGeo = new THREE.IcosahedronGeometry(2.8, 1);
        const coreMat = new THREE.MeshPhongMaterial({
            color: 0x051329,
            emissive: 0x00d4ff,
            emissiveIntensity: 0.6,
            specular: 0xffffff,
            shininess: 100,
            wireframe: false,
            transparent: true,
            opacity: 0.88
        });
        const vaultGem = new THREE.Mesh(coreGeo, coreMat);
        vaultGroup.add(vaultGem);

        // Glowing Wireframe Outer Lattice
        const wireGeo = new THREE.IcosahedronGeometry(3.2, 1);
        const wireMat = new THREE.MeshBasicMaterial({
            color: 0x00ff9d,
            wireframe: true,
            transparent: true,
            opacity: 0.45
        });
        const vaultWireframe = new THREE.Mesh(wireGeo, wireMat);
        vaultGroup.add(vaultWireframe);

        // 2. Orbiting Cryptographic Rings
        // Outer Ring: BLAKE2b 512-bit Ring
        const r1Geo = new THREE.TorusGeometry(6.2, 0.08, 16, 100);
        const r1Mat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.75
        });
        const ringBLAKE2b = new THREE.Mesh(r1Geo, r1Mat);
        ringBLAKE2b.rotation.x = Math.PI / 2;
        vaultGroup.add(ringBLAKE2b);

        // Middle Ring: SHA-256 Collision Resistant Ring
        const r2Geo = new THREE.TorusGeometry(8.2, 0.09, 16, 100);
        const r2Mat = new THREE.MeshBasicMaterial({
            color: 0x00ff9d,
            transparent: true,
            opacity: 0.65
        });
        const ringSHA256 = new THREE.Mesh(r2Geo, r2Mat);
        ringSHA256.rotation.x = Math.PI / 3;
        ringSHA256.rotation.y = Math.PI / 6;
        vaultGroup.add(ringSHA256);

        // Third Ring: Merkle Root & PBKDF2 Ring
        const r3Geo = new THREE.TorusGeometry(10.5, 0.07, 16, 100);
        const r3Mat = new THREE.MeshBasicMaterial({
            color: 0xffb703,
            transparent: true,
            opacity: 0.55
        });
        const ringMerkle = new THREE.Mesh(r3Geo, r3Mat);
        ringMerkle.rotation.x = -Math.PI / 4;
        vaultGroup.add(ringMerkle);

        // Register for smooth frame rotation
        Forensic3D.rotators.push({
            obj: vaultGem,
            rx: 0.005, ry: 0.008, rz: 0.003
        });
        Forensic3D.rotators.push({
            obj: vaultWireframe,
            rx: -0.004, ry: -0.007, rz: 0.002
        });
        Forensic3D.rotators.push({
            obj: ringBLAKE2b,
            rx: 0.001, ry: 0.002, rz: 0.008
        });
        Forensic3D.rotators.push({
            obj: ringSHA256,
            rx: -0.006, ry: 0.003, rz: -0.005
        });
        Forensic3D.rotators.push({
            obj: ringMerkle,
            rx: 0.004, ry: -0.005, rz: 0.002
        });

        // 3. Station Billboard / 3D Title Marker
        createStationMarker(vaultGroup, 'CRYPTOGRAPHIC VAULT MATRIX', 'AES-256-GCM ZERO-KNOWLEDGE REPOSITORY', 0x00f0ff, 12);

        scene.add(vaultGroup);
        Forensic3D.vaultGroup = vaultGroup;
    }

    // Dynamic Evidence Nodes Generator
    function renderEvidenceNodes(evidenceList) {
        const scene = Forensic3D.scene;

        // Clear existing nodes if any
        Forensic3D.evidenceNodes.forEach(node => {
            scene.remove(node.mesh);
            const idx = Forensic3D.interactiveObjects.indexOf(node.mesh);
            if (idx > -1) Forensic3D.interactiveObjects.splice(idx, 1);
        });
        Forensic3D.evidenceNodes = [];

        if (!evidenceList || evidenceList.length === 0) return;

        const count = evidenceList.length;
        const baseRadius = 13.5;

        evidenceList.forEach((ev, idx) => {
            const angle = (idx / count) * Math.PI * 2;
            const radius = baseRadius + (idx % 2 === 0 ? 1.5 : -1.5);
            const yOffset = (Math.sin(idx * 1.5) * 2.5);

            // Classification Colors
            let colorHex = 0x00f0ff; // Confidential
            if (ev.classification === 'Top Secret') colorHex = 0xff3366;
            else if (ev.classification === 'Secret') colorHex = 0xffb703;
            else if (ev.classification === 'Unclassified') colorHex = 0x00ff9d;

            // Crystal Polyhedron Geometry
            const geom = new THREE.OctahedronGeometry(1.0, 0);
            const mat = new THREE.MeshPhongMaterial({
                color: 0x041124,
                emissive: colorHex,
                emissiveIntensity: 0.65,
                specular: 0xffffff,
                shininess: 80,
                wireframe: false
            });
            const mesh = new THREE.Mesh(geom, mat);
            mesh.position.set(
                Math.cos(angle) * radius,
                yOffset,
                Math.sin(angle) * radius
            );

            // Glowing Wire Halo
            const haloGeom = new THREE.OctahedronGeometry(1.25, 0);
            const haloMat = new THREE.MeshBasicMaterial({
                color: colorHex,
                wireframe: true,
                transparent: true,
                opacity: 0.5
            });
            const haloMesh = new THREE.Mesh(haloGeom, haloMat);
            mesh.add(haloMesh);

            // Metadata linkage
            mesh.userData = {
                type: 'evidence_node',
                evidence: ev,
                originalColor: colorHex
            };

            scene.add(mesh);
            Forensic3D.interactiveObjects.push(mesh);

            // Node object with orbit math
            Forensic3D.evidenceNodes.push({
                mesh: mesh,
                angle: angle,
                radius: radius,
                yBase: yOffset,
                speed: 0.003 + (idx * 0.0005)
            });
        });
    }

    // =========================================================================
    // 5. STATION 2: 3D BLOCKCHAIN CHAIN-OF-CUSTODY HIGHWAY
    // =========================================================================
    function buildBlockchainHighway() {
        const scene = Forensic3D.scene;
        const chainGroup = new THREE.Group();
        chainGroup.position.set(65, 0, -42);

        createStationMarker(chainGroup, 'IMMUTABLE MERKLE BLOCKCHAIN', 'ISO/IEC 27037 CHAIN OF CUSTODY AUDIT TRAIL', 0x00ff9d, 12);
        scene.add(chainGroup);
        Forensic3D.chainGroup = chainGroup;
    }

    function renderBlockchainBlocks(blocks) {
        const chainGroup = Forensic3D.chainGroup;
        if (!chainGroup) return;

        // Clear existing blocks
        Forensic3D.blockchainBlocks.forEach(b => {
            chainGroup.remove(b.mesh);
            const idx = Forensic3D.interactiveObjects.indexOf(b.mesh);
            if (idx > -1) Forensic3D.interactiveObjects.splice(idx, 1);
        });
        Forensic3D.blockchainBlocks = [];

        // Remove old connecting laser line if any
        if (Forensic3D.chainLine) {
            chainGroup.remove(Forensic3D.chainLine);
            Forensic3D.chainLine = null;
        }

        if (!blocks || blocks.length === 0) return;

        const blockPositions = [];
        const spacing = 7.5;
        const startX = -((blocks.length - 1) * spacing) / 2;

        blocks.forEach((blk, idx) => {
            const x = startX + (idx * spacing);
            const y = Math.sin(idx * 0.8) * 1.5;
            const z = 0;
            const pos = new THREE.Vector3(x, y, z);
            blockPositions.push(pos);

            // Cube Box Geometry
            const bGeo = new THREE.BoxGeometry(2.8, 2.2, 2.8);
            const isGenesis = (idx === 0);
            const colorHex = isGenesis ? 0xffb703 : 0x00f0ff;

            const bMat = new THREE.MeshPhongMaterial({
                color: 0x051329,
                emissive: colorHex,
                emissiveIntensity: 0.45,
                specular: 0xffffff,
                shininess: 90,
                transparent: true,
                opacity: 0.85
            });
            const bMesh = new THREE.Mesh(bGeo, bMat);
            bMesh.position.copy(pos);

            // Wireframe Bevel Cage
            const edgeGeo = new THREE.EdgesGeometry(bGeo);
            const edgeMat = new THREE.LineBasicMaterial({
                color: colorHex,
                linewidth: 1.5
            });
            const wireMesh = new THREE.LineSegments(edgeGeo, edgeMat);
            bMesh.add(wireMesh);

            // Inner Pulsing Core
            const innerGeo = new THREE.SphereGeometry(0.5, 12, 12);
            const innerMat = new THREE.MeshBasicMaterial({
                color: colorHex
            });
            const innerCore = new THREE.Mesh(innerGeo, innerMat);
            bMesh.add(innerCore);

            bMesh.userData = {
                type: 'blockchain_block',
                block: blk,
                index: idx,
                originalColor: colorHex
            };

            chainGroup.add(bMesh);
            Forensic3D.interactiveObjects.push(bMesh);

            Forensic3D.blockchainBlocks.push({
                mesh: bMesh,
                block: blk,
                index: idx
            });
        });

        // Glowing Laser Line connecting all blocks
        if (blockPositions.length > 1) {
            const lineGeo = new THREE.BufferGeometry().setFromPoints(blockPositions);
            const lineMat = new THREE.LineBasicMaterial({
                color: 0x00ff9d,
                transparent: true,
                opacity: 0.75,
                linewidth: 2
            });
            const chainLine = new THREE.Line(lineGeo, lineMat);
            chainGroup.add(chainLine);
            Forensic3D.chainLine = chainLine;
        }
    }

    // =========================================================================
    // 6. STATION 3: 3D EVIDENCE INGESTION & ENCRYPTION PIPELINE
    // =========================================================================
    function buildIngestionPipeline() {
        const scene = Forensic3D.scene;
        const pipelineGroup = new THREE.Group();
        pipelineGroup.position.set(-65, 0, -42);

        createStationMarker(pipelineGroup, 'EVIDENCE INGESTION & CRYPTO PIPELINE', 'DUAL HASHING &bull; DEDUPLICATION &bull; AES-256-GCM', 0x00f0ff, 12);

        // 4 Processing Stages (Conduit Chambers)
        const stages = [
            { name: '1. ACQUISITION & HASH DEMUX', color: 0x00f0ff, x: -16 },
            { name: '2. DUAL HASH (SHA256+BLAKE2B)', color: 0x00ff9d, x: -5 },
            { name: '3. STORAGE DEDUPLICATION', color: 0xffb703, x: 6 },
            { name: '4. AES-256-GCM CIPHER SEAL', color: 0x8b5cf6, x: 17 }
        ];

        stages.forEach(st => {
            // Chamber Cylinder
            const cylGeo = new THREE.CylinderGeometry(2.0, 2.0, 3.8, 24, 1, true);
            const cylMat = new THREE.MeshPhongMaterial({
                color: 0x07152b,
                emissive: st.color,
                emissiveIntensity: 0.35,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.75
            });
            const cylMesh = new THREE.Mesh(cylGeo, cylMat);
            cylMesh.position.set(st.x, 0, 0);

            // Chamber Edge Rings
            const edgeR1 = new THREE.Mesh(
                new THREE.TorusGeometry(2.0, 0.08, 16, 32),
                new THREE.MeshBasicMaterial({ color: st.color })
            );
            edgeR1.rotation.x = Math.PI / 2;
            edgeR1.position.y = 1.9;
            cylMesh.add(edgeR1);

            const edgeR2 = edgeR1.clone();
            edgeR2.position.y = -1.9;
            cylMesh.add(edgeR2);

            pipelineGroup.add(cylMesh);
            Forensic3D.rotators.push({ obj: cylMesh, rx: 0, ry: 0.008, rz: 0 });
        });

        // Connecting Laser Pipeline Tubes
        const tubeGeo = new THREE.CylinderGeometry(0.35, 0.35, 36, 16);
        tubeGeo.rotateZ(Math.PI / 2);
        const tubeMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.55
        });
        const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
        tubeMesh.position.set(0.5, 0, 0);
        pipelineGroup.add(tubeMesh);

        // Animated Data Packets along the pipeline
        const packetCount = 24;
        const packetGeo = new THREE.SphereGeometry(0.35, 12, 12);
        const packetMat = new THREE.MeshBasicMaterial({ color: 0x00ff9d });
        const packetGroup = new THREE.Group();

        const packets = [];
        for (let i = 0; i < packetCount; i++) {
            const p = new THREE.Mesh(packetGeo, packetMat);
            p.position.set(-18 + (i * 1.5), 0, 0);
            packetGroup.add(p);
            packets.push(p);
        }
        pipelineGroup.add(packetGroup);
        Forensic3D.pipelinePackets = packets;

        scene.add(pipelineGroup);
        Forensic3D.pipelineGroup = pipelineGroup;
    }

    // =========================================================================
    // 7. STATION 4: 3D TAMPER DETECTION & QUARANTINE LAB
    // =========================================================================
    function buildTamperLabPlatform() {
        const scene = Forensic3D.scene;
        const labGroup = new THREE.Group();
        labGroup.position.set(0, 0, 60);

        createStationMarker(labGroup, 'TAMPER DETECTION & QUARANTINE LAB', 'ZERO-TRUST FORENSIC MERKLE AUDITOR', 0xff3366, 12);

        // Hexagonal Inspection Platform
        const hexGeo = new THREE.CylinderGeometry(8, 8.5, 0.8, 6);
        const hexMat = new THREE.MeshPhongMaterial({
            color: 0x071120,
            emissive: 0x112240,
            emissiveIntensity: 0.5,
            specular: 0x00f0ff,
            shininess: 60
        });
        const platform = new THREE.Mesh(hexGeo, hexMat);
        platform.position.y = -0.4;
        labGroup.add(platform);

        // Platform Border Warning Ring
        const ringGeo = new THREE.RingGeometry(8.1, 8.4, 6);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0xff3366,
            side: THREE.DoubleSide
        });
        const hexRing = new THREE.Mesh(ringGeo, ringMat);
        hexRing.rotation.x = Math.PI / 2;
        hexRing.position.y = 0.05;
        labGroup.add(hexRing);

        // Central Test Evidence Target
        const targetGeo = new THREE.BoxGeometry(2.4, 2.4, 2.4);
        const targetMat = new THREE.MeshPhongMaterial({
            color: 0x061830,
            emissive: 0x00f0ff,
            emissiveIntensity: 0.6,
            specular: 0xffffff
        });
        const testBlock = new THREE.Mesh(targetGeo, targetMat);
        testBlock.position.set(0, 1.8, 0);

        const edgeLines = new THREE.LineSegments(
            new THREE.EdgesGeometry(targetGeo),
            new THREE.LineBasicMaterial({ color: 0x00f0ff, linewidth: 2 })
        );
        testBlock.add(edgeLines);
        labGroup.add(testBlock);
        Forensic3D.testBlock = testBlock;
        Forensic3D.testBlockEdges = edgeLines;

        Forensic3D.rotators.push({ obj: testBlock, rx: 0.006, ry: 0.009, rz: 0.002 });

        // Quarantine Forcefield Dome (Hidden initially)
        const domeGeo = new THREE.SphereGeometry(4.2, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2);
        const domeMat = new THREE.MeshBasicMaterial({
            color: 0xff3366,
            wireframe: true,
            transparent: true,
            opacity: 0
        });
        const quarantineDome = new THREE.Mesh(domeGeo, domeMat);
        quarantineDome.position.y = 0;
        labGroup.add(quarantineDome);
        Forensic3D.quarantineDome = quarantineDome;

        scene.add(labGroup);
        Forensic3D.labGroup = labGroup;
    }

    // Tamper Attack Animation Simulator Triggered from HUD
    function trigger3DTamperSimulation() {
        if (Forensic3D.isTampered) return;
        Forensic3D.isTampered = true;

        playTamperAlarmSound();

        // Switch camera to Tamper Station
        switchStation('tamper');

        // Turn screen alarm banner on
        const banner = document.getElementById('tamper-banner-alert');
        if (banner) banner.style.display = 'block';

        // Add class to body for red vignette scanline alarm
        document.body.classList.add('tamper-alarm-active');

        // Turn test block into flashing crimson glitch
        if (Forensic3D.testBlock) {
            Forensic3D.testBlock.material.emissive.setHex(0xff0055);
            Forensic3D.testBlock.material.emissiveIntensity = 1.0;
        }
        if (Forensic3D.testBlockEdges) {
            Forensic3D.testBlockEdges.material.color.setHex(0xff0055);
        }

        // Deploy Zero-Trust Quarantine Dome
        if (Forensic3D.quarantineDome) {
            new TWEEN.Tween(Forensic3D.quarantineDome.material)
                .to({ opacity: 0.75 }, 800)
                .easing(TWEEN.Easing.Cubic.Out)
                .start();
        }

        // Flash Tamper Red Point Light
        if (Forensic3D.tamperLight) {
            new TWEEN.Tween(Forensic3D.tamperLight)
                .to({ intensity: 3.5 }, 500)
                .yoyo(true)
                .repeat(6)
                .start();
        }

        // Call backend simulate tamper endpoint for live sync
        fetch('/api/ledger/tamper', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                block_index: 1,
                malicious_action: 'UNAUTHORIZED_TAMPER_PAYLOAD_EVALUATOR_DEMO'
            })
        }).then(r => r.json()).then(res => {
            console.log('[3D TAMPER AUDIT LOGGED]', res);
            fetchLiveForensicData();
            show3DToast('⚠️ CRITICAL TAMPER ALERT: Block #1 integrity breach isolated!', 'danger');
        }).catch(err => {
            console.warn('Tamper API error:', err);
        });
    }
    window.trigger3DTamperSimulation = trigger3DTamperSimulation;

    // Tamper Self-Healing / Repair Chain Triggered from HUD
    function trigger3DRepairSimulation() {
        if (!Forensic3D.isTampered) {
            show3DToast('Ledger is already 100% cryptographically valid.', 'info');
            return;
        }

        playRepairChime();

        // Turn off alarm visual states
        Forensic3D.isTampered = false;
        document.body.classList.remove('tamper-alarm-active');

        const banner = document.getElementById('tamper-banner-alert');
        if (banner) banner.style.display = 'none';

        // Animate block back to healthy cyan/emerald
        if (Forensic3D.testBlock) {
            new TWEEN.Tween(Forensic3D.testBlock.material.emissive)
                .to({ r: 0.0, g: 0.94, b: 1.0 }, 1000)
                .start();
        }
        if (Forensic3D.testBlockEdges) {
            Forensic3D.testBlockEdges.material.color.setHex(0x00ff9d);
        }

        // Dissolve quarantine forcefield
        if (Forensic3D.quarantineDome) {
            new TWEEN.Tween(Forensic3D.quarantineDome.material)
                .to({ opacity: 0 }, 1000)
                .start();
        }

        if (Forensic3D.tamperLight) {
            Forensic3D.tamperLight.intensity = 0;
        }

        // Call backend repair endpoint
        fetch('/api/ledger/repair', { method: 'POST' })
            .then(r => r.json())
            .then(res => {
                console.log('[3D LEDGER REPAIR SUCCESS]', res);
                fetchLiveForensicData();
                show3DToast('🛡️ Cryptographic Self-Healing Complete: 100% Chain Integrity Restored!', 'success');
            }).catch(err => {
                console.warn('Repair API error:', err);
            });
    }
    window.trigger3DRepairSimulation = trigger3DRepairSimulation;

    // =========================================================================
    // 8. STATION 5: 3D STORAGE OPTIMIZATION MATRIX
    // =========================================================================
    function buildStorageMatrixComparison() {
        const scene = Forensic3D.scene;
        const storageGroup = new THREE.Group();
        storageGroup.position.set(0, 32, -72);

        createStationMarker(storageGroup, 'FORENSIC STORAGE OPTIMIZATION MATRIX', 'CONTENT-ADDRESSABLE DEDUPLICATION & LOSSLESS ZLIB', 0xffb703, 16);

        // 1. Raw Seized Evidence Volumetric Tower (TALL)
        const rawGroup = new THREE.Group();
        rawGroup.position.set(-10, 0, 0);

        const rawTowerGeo = new THREE.BoxGeometry(4.5, 18, 4.5);
        const rawTowerMat = new THREE.MeshPhongMaterial({
            color: 0x1f2937,
            emissive: 0xff3366,
            emissiveIntensity: 0.25,
            wireframe: false,
            transparent: true,
            opacity: 0.8
        });
        const rawMesh = new THREE.Mesh(rawTowerGeo, rawTowerMat);
        rawMesh.position.y = 9;
        rawGroup.add(rawMesh);

        // Edge lines on raw tower
        rawMesh.add(new THREE.LineSegments(
            new THREE.EdgesGeometry(rawTowerGeo),
            new THREE.LineBasicMaterial({ color: 0xff3366 })
        ));
        storageGroup.add(rawGroup);

        // 2. Cryptographically Optimized Vault Tower (COMPACT & SLEEK)
        const optGroup = new THREE.Group();
        optGroup.position.set(10, 0, 0);

        const optTowerGeo = new THREE.BoxGeometry(4.5, 4.5, 4.5);
        const optTowerMat = new THREE.MeshPhongMaterial({
            color: 0x052e16,
            emissive: 0x00ff9d,
            emissiveIntensity: 0.6,
            wireframe: false,
            transparent: true,
            opacity: 0.9
        });
        const optMesh = new THREE.Mesh(optTowerGeo, optTowerMat);
        optMesh.position.y = 2.25;
        optGroup.add(optMesh);

        optMesh.add(new THREE.LineSegments(
            new THREE.EdgesGeometry(optTowerGeo),
            new THREE.LineBasicMaterial({ color: 0x00ff9d, linewidth: 2 })
        ));
        storageGroup.add(optGroup);

        // 3. Central Arrow / Reduction Beam
        const beamGeo = new THREE.CylinderGeometry(0.2, 0.2, 14, 16);
        beamGeo.rotateZ(Math.PI / 2);
        const beamMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
        const beam = new THREE.Mesh(beamGeo, beamMat);
        beam.position.set(0, 5, 0);
        storageGroup.add(beam);

        scene.add(storageGroup);
        Forensic3D.storageGroup = storageGroup;
    }

    // =========================================================================
    // 9. 3D STATION MARKER / BILLBOARD UTILITY
    // =========================================================================
    function createStationMarker(parentGroup, title, subtitle, colorHex, yOffset) {
        // High-res HTML5 Canvas text texture
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = 'rgba(11, 17, 32, 0.85)';
        ctx.strokeStyle = '#' + colorHex.toString(16).padStart(6, '0');
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.roundRect(10, 10, 1004, 236, 24);
        ctx.fill();
        ctx.stroke();

        // Title text
        ctx.font = 'bold 44px Outfit, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText(title, 512, 100);

        // Subtitle text
        ctx.font = '500 24px "JetBrains Mono", monospace';
        ctx.fillStyle = '#' + colorHex.toString(16).padStart(6, '0');
        ctx.fillText(subtitle, 512, 165);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMat = new THREE.SpriteMaterial({
            map: texture,
            transparent: true,
            opacity: 0.95
        });
        const sprite = new THREE.Sprite(spriteMat);
        sprite.scale.set(18, 4.5, 1);
        sprite.position.y = yOffset;
        parentGroup.add(sprite);
    }

    // =========================================================================
    // 10. INTERACTION, RAYCASTING & CLICK INSPECTOR
    // =========================================================================
    function setupInteractionListeners() {
        const dom = Forensic3D.renderer.domElement;

        dom.addEventListener('mousemove', onPointerMove, false);
        dom.addEventListener('click', onPointerClick, false);
    }

    function onPointerMove(event) {
        Forensic3D.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        Forensic3D.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        Forensic3D.raycaster.setFromCamera(Forensic3D.mouse, Forensic3D.camera);
        const intersects = Forensic3D.raycaster.intersectObjects(Forensic3D.interactiveObjects, false);

        if (intersects.length > 0) {
            const hit = intersects[0].object;
            if (Forensic3D.hoveredObject !== hit) {
                // Reset previous
                if (Forensic3D.hoveredObject && Forensic3D.hoveredObject.scale) {
                    Forensic3D.hoveredObject.scale.set(1, 1, 1);
                }
                Forensic3D.hoveredObject = hit;
                hit.scale.set(1.25, 1.25, 1.25);
                document.body.style.cursor = 'pointer';
                playLaserPing(900, 0.05);
            }
        } else {
            if (Forensic3D.hoveredObject && Forensic3D.hoveredObject.scale) {
                Forensic3D.hoveredObject.scale.set(1, 1, 1);
            }
            Forensic3D.hoveredObject = null;
            document.body.style.cursor = 'default';
        }
    }

    function onPointerClick(event) {
        Forensic3D.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        Forensic3D.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        Forensic3D.raycaster.setFromCamera(Forensic3D.mouse, Forensic3D.camera);
        const intersects = Forensic3D.raycaster.intersectObjects(Forensic3D.interactiveObjects, false);

        if (intersects.length > 0) {
            const hit = intersects[0].object;
            playLaserPing(1200, 0.12);

            if (hit.userData.type === 'evidence_node') {
                showEvidenceCard(hit.userData.evidence, hit.position);
            } else if (hit.userData.type === 'blockchain_block') {
                showBlockInspector(hit.userData.block, hit.position);
            }
        }
    }

    // Evidence Hologram Card Popup
    function showEvidenceCard(ev, pos) {
        Forensic3D.selectedEvidence = ev;
        const card = document.getElementById('holo-evidence-card');
        if (!card) return;

        document.getElementById('card-ev-id').innerText = ev.evidence_id || 'EV-UNKNOWN';
        document.getElementById('card-ev-case').innerText = ev.case_id || 'N/A';
        document.getElementById('card-ev-file').innerText = ev.filename || 'N/A';
        document.getElementById('card-ev-custodian').innerText = ev.custodian || 'N/A';
        document.getElementById('card-ev-ratio').innerText = `${ev.compression_ratio_pct}% (${ev.vault_size_bytes}B / ${ev.raw_size_bytes}B)`;
        document.getElementById('card-ev-sha256').innerText = ev.content_hash || 'SHA-256 Digest';
        document.getElementById('card-ev-blake2b').innerText = ev.blake2b_hash || 'BLAKE2b Digest';

        const badge = document.getElementById('card-ev-badge');
        badge.innerText = ev.classification || 'Confidential';
        badge.style.color = (ev.classification === 'Top Secret') ? '#ff3366' : '#00ff9d';

        card.classList.remove('hidden');

        // Smooth camera zoom towards clicked evidence
        if (pos) {
            const worldPos = new THREE.Vector3();
            Forensic3D.scene.localToWorld(worldPos.copy(pos));
            new TWEEN.Tween(Forensic3D.controls.target)
                .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, 800)
                .easing(TWEEN.Easing.Cubic.Out)
                .start();
        }
    }

    function closeEvidenceCard() {
        const card = document.getElementById('holo-evidence-card');
        if (card) card.classList.add('hidden');
    }
    window.closeEvidenceCard = closeEvidenceCard;

    // Verify Selected Evidence from 3D HUD
    function verifySelectedEvidence() {
        if (!Forensic3D.selectedEvidence) return;
        const id = Forensic3D.selectedEvidence.evidence_id;

        playLaserPing(1000, 0.15);
        show3DToast(`Initiating zero-trust audit for ${id}...`, 'info');

        fetch(`/api/evidence/verify/${id}`)
            .then(r => r.json())
            .then(report => {
                if (report.integrity_valid) {
                    playRepairChime();
                    show3DToast(`✅ INTEGRITY VERIFIED: SHA-256 & BLAKE2b validated with zero tampering.`, 'success');
                } else {
                    playTamperAlarmSound();
                    show3DToast(`❌ TAMPER DETECTED: Evidence digest mismatch!`, 'danger');
                }
            }).catch(e => {
                show3DToast(`Verification error: ${e.message}`, 'danger');
            });
    }
    window.verifySelectedEvidence = verifySelectedEvidence;

    // Download Decrypted Evidence from 3D HUD
    function downloadSelectedEvidence() {
        if (!Forensic3D.selectedEvidence) return;
        const id = Forensic3D.selectedEvidence.evidence_id;
        playLaserPing(750, 0.1);
        window.open(`/api/evidence/download/${id}?requestor=3D_Forensic_Operator`, '_blank');
        show3DToast(`Decryption authorization granted for ${id}. Commencing download.`, 'info');
    }
    window.downloadSelectedEvidence = downloadSelectedEvidence;

    // View Official Court Certificate
    function viewSelectedCertificate() {
        if (!Forensic3D.selectedEvidence) return;
        const id = Forensic3D.selectedEvidence.evidence_id;
        window.open(`/api/certificate/${id}`, '_blank');
    }
    window.viewSelectedCertificate = viewSelectedCertificate;

    // Blockchain Block Inspector
    function showBlockInspector(blk, pos) {
        show3DToast(`Block #${blk.index} [${blk.action}] by ${blk.custodian}`, 'info');
        if (pos && Forensic3D.chainGroup) {
            const worldPos = new THREE.Vector3();
            Forensic3D.chainGroup.localToWorld(worldPos.copy(pos));
            new TWEEN.Tween(Forensic3D.controls.target)
                .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, 800)
                .easing(TWEEN.Easing.Cubic.Out)
                .start();
        }
    }

    // =========================================================================
    // 11. NAVIGATION & STATION SWITCHER (CAMERA TWEENING)
    // =========================================================================
    function switchStation(stationName) {
        if (!Forensic3D.stations[stationName]) return;
        Forensic3D.currentStation = stationName;

        playLaserPing(700, 0.08);

        // Update active class on dock buttons
        document.querySelectorAll('.station-dock-btn').forEach(btn => {
            if (btn.getAttribute('data-station') === stationName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        const targetStation = Forensic3D.stations[stationName];

        // Smooth Camera Position Tween
        new TWEEN.Tween(Forensic3D.camera.position)
            .to({
                x: targetStation.camPos.x,
                y: targetStation.camPos.y,
                z: targetStation.camPos.z
            }, 1200)
            .easing(TWEEN.Easing.Cubic.InOut)
            .start();

        // Smooth Controls Target Tween
        new TWEEN.Tween(Forensic3D.controls.target)
            .to({
                x: targetStation.target.x,
                y: targetStation.target.y,
                z: targetStation.target.z
            }, 1200)
            .easing(TWEEN.Easing.Cubic.InOut)
            .start();
    }
    window.switch3DStation = switchStation;

    // Cinematic Flythrough Tour Mode
    function toggleCinematicTour() {
        Forensic3D.isCinematic = !Forensic3D.isCinematic;
        const banner = document.getElementById('cinematic-banner');
        const btn = document.getElementById('btn-cinematic-tour');

        if (Forensic3D.isCinematic) {
            if (banner) banner.style.display = 'block';
            if (btn) btn.classList.add('active');
            show3DToast('Cinematic flythrough mode activated.', 'info');
            runCinematicCycle();
        } else {
            if (banner) banner.style.display = 'none';
            if (btn) btn.classList.remove('active');
            clearTimeout(Forensic3D.cinematicTimer);
            show3DToast('Cinematic flythrough paused.', 'info');
        }
    }
    window.toggleCinematicTour = toggleCinematicTour;

    function runCinematicCycle() {
        if (!Forensic3D.isCinematic) return;
        const stationOrder = ['vault', 'blockchain', 'ingest', 'tamper', 'storage'];
        let currentIdx = stationOrder.indexOf(Forensic3D.currentStation);
        let nextIdx = (currentIdx + 1) % stationOrder.length;
        switchStation(stationOrder[nextIdx]);

        Forensic3D.cinematicTimer = setTimeout(() => {
            runCinematicCycle();
        }, 7500);
    }

    // Reset Camera
    function resetCamera() {
        switchStation('vault');
    }
    window.reset3DCamera = resetCamera;

    // =========================================================================
    // 12. SWITCH BETWEEN 3D EXPERIENCE AND 2D CONSOLE VIEW
    // =========================================================================
    function toggleForensicMode(mode) {
        const viewport = document.getElementById('webgl-viewport-wrapper');
        const mainNav = document.querySelector('.nav-container');
        const mainContainer = document.querySelector('main.container');
        const header = document.querySelector('header');
        const topStatusBar = document.querySelector('.top-status-bar');

        if (mode === '2d') {
            // Switch to 2D Forensic Console
            if (viewport) viewport.classList.add('hidden');
            if (mainNav) mainNav.style.display = 'flex';
            if (mainContainer) mainContainer.style.display = 'block';
            if (header) header.style.display = 'flex';
            if (topStatusBar) topStatusBar.style.display = 'flex';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            // Switch to 3D Holographic Command Center
            if (viewport) viewport.classList.remove('hidden');
            if (mainNav) mainNav.style.display = 'none';
            if (mainContainer) mainContainer.style.display = 'none';
            if (header) header.style.display = 'none';
            if (topStatusBar) topStatusBar.style.display = 'none';
            switchStation('vault');
        }
    }
    window.toggleForensicMode = toggleForensicMode;

    // 3D Ingestion Modal Toggle
    function open3DIngestModal() {
        playLaserPing(850, 0.1);
        const modal = document.getElementById('holo-ingest-overlay');
        if (modal) modal.classList.remove('hidden');
    }
    window.open3DIngestModal = open3DIngestModal;

    function close3DIngestModal() {
        const modal = document.getElementById('holo-ingest-overlay');
        if (modal) modal.classList.add('hidden');
    }
    window.close3DIngestModal = close3DIngestModal;

    // Submit Evidence from 3D Ingest Form
    function handle3DIngestSubmit(event) {
        event.preventDefault();
        const fileInput = document.getElementById('ingest-3d-file');
        const caseInput = document.getElementById('ingest-3d-case');
        const classInput = document.getElementById('ingest-3d-classification');
        const notesInput = document.getElementById('ingest-3d-notes');

        if (!fileInput || !fileInput.files[0]) {
            show3DToast('Please select a digital evidence artifact file.', 'danger');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('case_id', caseInput.value || 'CASE-2026-3D');
        formData.append('classification', classInput.value || 'Confidential');
        formData.append('custodian', 'Special Agent Miller (3D Operator)');
        formData.append('notes', notesInput.value || 'Acquired via 3D Holographic Command Ingestion');

        show3DToast('⚡ Ingesting artifact into 3D cryptographic pipeline...', 'info');
        switchStation('ingest');

        fetch('/api/evidence/upload', {
            method: 'POST',
            body: formData
        }).then(r => r.json()).then(data => {
            if (data.success) {
                playRepairChime();
                close3DIngestModal();
                show3DToast(`✅ Vault Ingestion Succeeded! New block appended to chain.`, 'success');
                fetchLiveForensicData();
                setTimeout(() => switchStation('vault'), 1800);
            } else {
                show3DToast(`Upload failed: ${data.detail || 'Unknown error'}`, 'danger');
            }
        }).catch(err => {
            show3DToast(`Upload error: ${err.message}`, 'danger');
        });
    }
    window.handle3DIngestSubmit = handle3DIngestSubmit;

    // 3D Toast Notification
    function show3DToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        if (!toast) return;
        toast.innerText = msg;
        toast.style.borderColor = (type === 'danger') ? '#ff3366' : (type === 'success') ? '#00ff9d' : '#00f0ff';
        toast.style.boxShadow = `0 0 20px ${toast.style.borderColor}`;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 4000);
    }
    window.show3DToast = show3DToast;

    // =========================================================================
    // 13. DATA FETCHING & SYNCHRONIZATION WITH BACKEND
    // =========================================================================
    function fetchLiveForensicData() {
        // 1. Stats
        fetch('/api/stats')
            .then(r => r.json())
            .then(stats => {
                const countEl = document.getElementById('hud-stat-count');
                const ratioEl = document.getElementById('hud-stat-ratio');
                const savedEl = document.getElementById('hud-stat-saved');
                if (countEl) countEl.innerText = stats.total_evidence_files || 0;
                if (ratioEl) ratioEl.innerText = `${stats.space_savings_pct || 0}%`;
                if (savedEl) savedEl.innerText = `${stats.space_saved_bytes || 0} B`;
            }).catch(e => console.warn('Stats fetch failed:', e));

        // 2. Evidence List
        fetch('/api/evidence/list')
            .then(r => r.json())
            .then(list => {
                renderEvidenceNodes(list);
            }).catch(e => console.warn('Evidence fetch failed:', e));

        // 3. Blockchain Blocks
        fetch('/api/ledger/blocks')
            .then(r => r.json())
            .then(blocks => {
                renderBlockchainBlocks(blocks);
            }).catch(e => console.warn('Blocks fetch failed:', e));

        // 4. System Hash Monitor Stream
        fetch('/api/ledger/validate')
            .then(r => r.json())
            .then(audit => {
                const stream = document.getElementById('hud-hash-stream');
                if (stream) {
                    stream.innerHTML = `MERKLE ROOT: ${audit.merkle_root || 'N/A'}<br>` +
                        `STATUS: ${audit.valid ? '✅ ALL BLOCKS VALID' : '⚠️ CHAIN BREACH DETECTED'}<br>` +
                        `BLOCKS SCANNED: ${audit.block_count || 0}`;
                }
            }).catch(e => console.warn('Validation fetch failed:', e));
    }

    // =========================================================================
    // 14. UI EVENT LISTENERS
    // =========================================================================
    function setupUIEventListeners() {
        // Station dock buttons
        document.querySelectorAll('.station-dock-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const st = btn.getAttribute('data-station');
                if (st) switchStation(st);
            });
        });

        // 3D Ingest File Drag-and-drop
        const dropBox = document.getElementById('holo-drop-box');
        const fileInput = document.getElementById('ingest-3d-file');
        if (dropBox && fileInput) {
            dropBox.addEventListener('click', () => fileInput.click());
            dropBox.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropBox.classList.add('dragover');
            });
            dropBox.addEventListener('dragleave', () => dropBox.classList.remove('dragover'));
            dropBox.addEventListener('drop', (e) => {
                e.preventDefault();
                dropBox.classList.remove('dragover');
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    document.getElementById('ingest-3d-filename').innerText = fileInput.files[0].name;
                }
            });
            fileInput.addEventListener('change', () => {
                if (fileInput.files.length) {
                    document.getElementById('ingest-3d-filename').innerText = fileInput.files[0].name;
                }
            });
        }
    }

    // =========================================================================
    // 15. MAIN RENDER / ANIMATION LOOP
    // =========================================================================
    function animate() {
        requestAnimationFrame(animate);

        const delta = Forensic3D.clock.getDelta();
        const elapsedTime = Forensic3D.clock.getElapsedTime();

        // Update TWEEN transitions
        TWEEN.update();

        // Update Orbit Controls
        if (Forensic3D.controls) {
            Forensic3D.controls.update();
        }

        // Rotators update
        Forensic3D.rotators.forEach(item => {
            if (item.obj) {
                if (item.rx) item.obj.rotation.x += item.rx;
                if (item.ry) item.obj.rotation.y += item.ry;
                if (item.rz) item.obj.rotation.z += item.rz;
            }
        });

        // Orbiting Evidence Nodes Math
        Forensic3D.evidenceNodes.forEach(node => {
            node.angle += node.speed;
            node.mesh.position.x = Math.cos(node.angle) * node.radius;
            node.mesh.position.z = Math.sin(node.angle) * node.radius;
            node.mesh.position.y = node.yBase + Math.sin(elapsedTime * 2 + node.angle) * 0.4;
            node.mesh.rotation.y += 0.02;
            node.mesh.rotation.x += 0.01;
        });

        // Ingestion Pipeline Particle Stream
        if (Forensic3D.pipelinePackets) {
            Forensic3D.pipelinePackets.forEach((p, i) => {
                p.position.x += 0.08;
                if (p.position.x > 18) {
                    p.position.x = -18;
                }
            });
        }

        // Starfield Dust Drift
        if (Forensic3D.dataParticles) {
            Forensic3D.dataParticles.rotation.y = elapsedTime * 0.015;
            Forensic3D.dataParticles.rotation.x = Math.sin(elapsedTime * 0.01) * 0.02;
        }

        // Core light breathing pulse
        if (Forensic3D.coreLight) {
            Forensic3D.coreLight.intensity = 2.2 + Math.sin(elapsedTime * 3) * 0.6;
        }

        // Render Scene
        if (Forensic3D.renderer && Forensic3D.scene && Forensic3D.camera) {
            Forensic3D.renderer.render(Forensic3D.scene, Forensic3D.camera);
        }
    }

})();
