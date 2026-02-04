import React, { useEffect, useRef, useState } from "react";
import { AuroraRing } from "../candy/Candy";

type AvatarLifeControllerProps = {
  isSpeaking: boolean;
  expression?: { mood?: string } | null;
  children?: React.ReactNode;
};

const randomBetween = (min: number, max: number) => Math.random() * (max - min) + min;

export const AvatarLifeController = ({ isSpeaking, expression }: AvatarLifeControllerProps) => {
  const avatarRef = useRef<HTMLDivElement | null>(null);
  const isSpeakingRef = useRef(isSpeaking);
  const [debugState, setDebugState] = useState({ blinkCount: 0, idleSeconds: 0, active: false });

  useEffect(() => {
    isSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  useEffect(() => {
    const element = avatarRef.current;
    if (!element) return undefined;

    let rafId = 0;
    let lastUpdate = performance.now();
    let lastInteraction = performance.now();
    let lastDebugUpdate = 0;

    let blinkStart: number | null = null;
    let blinkCount = 0;
    let nextBlinkIn = randomBetween(2000, 7000);

    let gazeTarget = { x: 0, y: 0 };
    let gazeCurrent = { x: 0, y: 0 };
    let nextGazeShiftAt = performance.now() + randomBetween(500, 1800);

    let mouthOpen = 0.2;

    const updateLastInteraction = () => {
      lastInteraction = performance.now();
    };

    const shouldStopLife = () => {
      const animationsDisabled =
        localStorage.getItem("etherea.avatar.animations") === "disabled" ||
        document.body?.dataset?.avatarAnimations === "disabled";
      const safeMode =
        Boolean((window as typeof window & { __ETHEREA_SAFE_MODE?: boolean }).__ETHEREA_SAFE_MODE) ||
        document.body?.dataset?.safeMode === "true";
      const shuttingDown =
        document.body?.dataset?.appState === "closing" ||
        Boolean((window as typeof window & { __ETHEREA_CLOSING?: boolean }).__ETHEREA_CLOSING);
      return animationsDisabled || safeMode || shuttingDown;
    };

    const onFrame = (now: number) => {
      const delta = Math.min(64, now - lastUpdate);
      lastUpdate = now;

      const stopLife = shouldStopLife();
      element.dataset.lifeActive = stopLife ? "false" : "true";

      if (!stopLife) {
        const idleMs = now - lastInteraction;
        const idleSeconds = Math.floor(idleMs / 1000);
        const engagement = Math.max(0.2, 1 - idleMs / 45000);

        const breathRate = 3.8 + (1 - engagement) * 1.6;
        const breath = 0.5 + 0.5 * Math.sin((now / 1000) * (Math.PI * 2) / breathRate);

        const driftX = Math.sin(now / 1400) * (1.4 + engagement * 1.4);
        const driftY = Math.cos(now / 1900) * (1.2 + engagement * 1.2);

        if (now >= nextGazeShiftAt) {
          gazeTarget = {
            x: randomBetween(-2.5, 2.5) * engagement,
            y: randomBetween(-1.5, 1.5) * engagement,
          };
          nextGazeShiftAt = now + randomBetween(700, 2200);
        }

        const gazeLerp = 1 - Math.pow(0.001, delta / 1000);
        gazeCurrent = {
          x: gazeCurrent.x + (gazeTarget.x - gazeCurrent.x) * gazeLerp,
          y: gazeCurrent.y + (gazeTarget.y - gazeCurrent.y) * gazeLerp,
        };

        if (blinkStart === null) {
          if (now - lastInteraction > 0 && now - (lastUpdate - delta) >= nextBlinkIn) {
            blinkStart = now;
            blinkCount += 1;
            nextBlinkIn = randomBetween(2000, 7000);
          }
        }

        let blinkAmount = 0;
        if (blinkStart !== null) {
          const blinkProgress = (now - blinkStart) / 160;
          if (blinkProgress >= 1) {
            blinkStart = null;
          } else {
            blinkAmount = Math.sin(blinkProgress * Math.PI);
          }
        }

        const idleMouth = 0.22 + 0.05 * Math.sin(now / 1200);
        const speechOverlay = isSpeakingRef.current
          ? 0.35 + 0.15 * Math.sin(now / 120)
          : 0;
        const mouthTarget = Math.min(1, idleMouth + speechOverlay);
        const mouthLerp = 1 - Math.pow(0.002, delta / 1000);
        mouthOpen = mouthOpen + (mouthTarget - mouthOpen) * mouthLerp;

        element.style.setProperty("--breath", breath.toFixed(3));
        element.style.setProperty("--head-x", `${driftX.toFixed(2)}px`);
        element.style.setProperty("--head-y", `${driftY.toFixed(2)}px`);
        element.style.setProperty("--gaze-x", `${gazeCurrent.x.toFixed(2)}px`);
        element.style.setProperty("--gaze-y", `${gazeCurrent.y.toFixed(2)}px`);
        element.style.setProperty("--blink", blinkAmount.toFixed(3));
        element.style.setProperty("--mouth-open", mouthOpen.toFixed(3));

        if (now - lastDebugUpdate > 250) {
          lastDebugUpdate = now;
          setDebugState({ blinkCount, idleSeconds, active: true });
        }
      } else if (now - lastDebugUpdate > 500) {
        lastDebugUpdate = now;
        setDebugState((prev) => ({ ...prev, active: false }));
      }

      rafId = requestAnimationFrame(onFrame);
    };

    const events = ["pointerdown", "mousemove", "keydown", "focus"] as const;
    events.forEach((eventName) => window.addEventListener(eventName, updateLastInteraction));

    rafId = requestAnimationFrame(onFrame);

    return () => {
      cancelAnimationFrame(rafId);
      events.forEach((eventName) => window.removeEventListener(eventName, updateLastInteraction));
    };
  }, []);

  const isDebug =
    localStorage.getItem("etherea.avatar.debug") === "true" ||
    document.body?.dataset?.avatarDebug === "true";

  return (
    <div className="avatar-life" ref={avatarRef}>
      <div className="avatar-head">
        <AuroraRing isSpeaking={isSpeaking} expression={expression ?? undefined} />
        <div className="avatar-face">
          <div className="avatar-eye left">
            <span className="avatar-pupil" />
          </div>
          <div className="avatar-eye right">
            <span className="avatar-pupil" />
          </div>
          <div className="avatar-mouth" />
          <div className="avatar-cheek left" />
          <div className="avatar-cheek right" />
        </div>
      </div>
      {isDebug && (
        <div className="avatar-life-debug">
          <div>Avatar Life Loop: {debugState.active ? "ACTIVE" : "PAUSED"}</div>
          <div>Blinks: {debugState.blinkCount}</div>
          <div>Idle: {debugState.idleSeconds}s</div>
        </div>
      )}
    </div>
  );
};
