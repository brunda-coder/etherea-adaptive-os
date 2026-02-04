import React, { useEffect, useRef, useState } from "react";
import { AuroraRing } from "../candy/Candy";

type AvatarLifeControllerProps = {
  isSpeaking: boolean;
  expression?: { mood?: string } | null;
  children?: React.ReactNode;
};

const randomBetween = (min: number, max: number) => Math.random() * (max - min) + min;
const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

export const AvatarLifeController = ({ isSpeaking, expression }: AvatarLifeControllerProps) => {
  const avatarRef = useRef<HTMLDivElement | null>(null);
  const isSpeakingRef = useRef(isSpeaking);
  const [debugState, setDebugState] = useState({
    blinkCount: 0,
    idleSeconds: 0,
    active: false,
    spatialMode: "anchored-left",
    expression: "idle",
  });

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
    let spatialMode = "anchored-left";
    let nextSpatialShiftAt = performance.now() + randomBetween(5000, 9000);
    let surpriseCooldownUntil = 0;
    let lastPresenceMessage = "";

    let spatialCurrent = { x: 36, y: 360, tilt: 0, peek: 0, scale: 1 };
    let spatialTarget = { ...spatialCurrent };

    const updateLastInteraction = () => {
      lastInteraction = performance.now();
    };

    const getPresenceMessage = (mode: string, reason: string) => {
      if (reason === "surprise") {
        return "I peeked in gently to see how you're doing.";
      }
      switch (mode) {
        case "anchored-right":
          return "I moved over so I don't crowd your view.";
        case "anchored-left":
          return "I'm staying close on the left if you need me.";
        case "top-left":
        case "top-right":
          return "I'm up here watching over the workspace.";
        case "center-float":
          return "I'm floating nearby to guide you.";
        case "edge-peek-left":
        case "edge-peek-right":
          return "I'm just peeking in—wave if you want help.";
        default:
          return "I'm here, ready to help when you are.";
      }
    };

    const dispatchPresence = (message: string, mode: string, reason: string) => {
      if (!message || message === lastPresenceMessage) return;
      lastPresenceMessage = message;
      window.dispatchEvent(
        new CustomEvent("etherea:avatar-presence", { detail: { message, mode, reason } }),
      );
    };

    const resolveSpatialTarget = (mode: string) => {
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const anchorWidth = 320;
      const anchorHeight = 180;
      const marginX = 28;
      const marginY = 24;

      const safeX = (x: number) =>
        clamp(x, -anchorWidth * 0.45, viewportWidth - anchorWidth * 0.55);
      const safeY = (y: number) =>
        clamp(y, marginY, viewportHeight - anchorHeight - marginY);

      switch (mode) {
        case "anchored-right":
          return {
            x: safeX(viewportWidth - anchorWidth - marginX),
            y: safeY(viewportHeight * 0.62),
            tilt: -2.5,
            peek: 6,
            scale: 1,
          };
        case "top-left":
          return {
            x: safeX(marginX),
            y: safeY(marginY),
            tilt: 1.5,
            peek: 0,
            scale: 0.96,
          };
        case "top-right":
          return {
            x: safeX(viewportWidth - anchorWidth - marginX),
            y: safeY(marginY),
            tilt: -1.5,
            peek: 0,
            scale: 0.96,
          };
        case "center-float":
          return {
            x: safeX(viewportWidth * 0.5 - anchorWidth / 2),
            y: safeY(viewportHeight * 0.45 - anchorHeight / 2),
            tilt: 0,
            peek: 0,
            scale: 1.03,
          };
        case "edge-peek-left":
          return {
            x: safeX(-anchorWidth * 0.25),
            y: safeY(viewportHeight * 0.55),
            tilt: 2.5,
            peek: 12,
            scale: 0.98,
          };
        case "edge-peek-right":
          return {
            x: safeX(viewportWidth - anchorWidth * 0.75),
            y: safeY(viewportHeight * 0.35),
            tilt: -2.5,
            peek: -12,
            scale: 0.98,
          };
        case "anchored-left":
        default:
          return {
            x: safeX(marginX),
            y: safeY(viewportHeight * 0.62),
            tilt: 2,
            peek: 0,
            scale: 1,
          };
      }
    };

    const updateSpatialMode = (now: number, idleMs: number) => {
      if (now < nextSpatialShiftAt) return;

      const idleSeconds = Math.floor(idleMs / 1000);
      const isQuiet = idleSeconds >= 8 && !isSpeakingRef.current;
      const hasSurprise = idleSeconds >= 22 && now >= surpriseCooldownUntil && !isSpeakingRef.current;

      let nextMode = spatialMode;
      let reason = "drift";

      if (hasSurprise) {
        nextMode = spatialMode.includes("right") ? "edge-peek-left" : "edge-peek-right";
        reason = "surprise";
        surpriseCooldownUntil = now + randomBetween(45000, 70000);
        nextSpatialShiftAt = now + randomBetween(9000, 14000);
      } else if (isQuiet) {
        const options = ["top-left", "top-right", "center-float", "anchored-left", "anchored-right"];
        nextMode = options[Math.floor(randomBetween(0, options.length))];
        nextSpatialShiftAt = now + randomBetween(7000, 12000);
      } else {
        nextMode = spatialMode === "anchored-left" ? "anchored-right" : "anchored-left";
        nextSpatialShiftAt = now + randomBetween(8000, 13000);
      }

      if (nextMode !== spatialMode) {
        spatialMode = nextMode;
        spatialTarget = resolveSpatialTarget(spatialMode);
        dispatchPresence(getPresenceMessage(spatialMode, reason), spatialMode, reason);
        const parent = element.parentElement as HTMLElement | null;
        if (parent) {
          parent.dataset.avatarMode = spatialMode;
          parent.dataset.avatarOrient = spatialMode.includes("right") ? "right" : "left";
        }
      }
    };

    spatialTarget = resolveSpatialTarget(spatialMode);
    spatialCurrent = { ...spatialTarget };
    const parent = element.parentElement as HTMLElement | null;
    if (parent) {
      parent.dataset.avatarMode = spatialMode;
      parent.dataset.avatarOrient = spatialMode.includes("right") ? "right" : "left";
    }
    dispatchPresence(getPresenceMessage(spatialMode, "init"), spatialMode, "init");

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

        updateSpatialMode(now, idleMs);

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

        const spatialLerp = 1 - Math.pow(0.0015, delta / 1000);
        spatialCurrent = {
          x: spatialCurrent.x + (spatialTarget.x - spatialCurrent.x) * spatialLerp,
          y: spatialCurrent.y + (spatialTarget.y - spatialCurrent.y) * spatialLerp,
          tilt: spatialCurrent.tilt + (spatialTarget.tilt - spatialCurrent.tilt) * spatialLerp,
          peek: spatialCurrent.peek + (spatialTarget.peek - spatialCurrent.peek) * spatialLerp,
          scale: spatialCurrent.scale + (spatialTarget.scale - spatialCurrent.scale) * spatialLerp,
        };

        const parent = element.parentElement as HTMLElement | null;
        const targetElement = parent ?? element;
        targetElement.style.setProperty("--avatar-x", `${spatialCurrent.x.toFixed(1)}px`);
        targetElement.style.setProperty("--avatar-y", `${spatialCurrent.y.toFixed(1)}px`);
        targetElement.style.setProperty("--avatar-tilt", `${spatialCurrent.tilt.toFixed(2)}deg`);
        targetElement.style.setProperty("--avatar-peek", `${spatialCurrent.peek.toFixed(1)}px`);
        targetElement.style.setProperty("--avatar-scale", spatialCurrent.scale.toFixed(3));

        element.style.setProperty("--breath", breath.toFixed(3));
        element.style.setProperty("--head-x", `${driftX.toFixed(2)}px`);
        element.style.setProperty("--head-y", `${driftY.toFixed(2)}px`);
        element.style.setProperty("--gaze-x", `${gazeCurrent.x.toFixed(2)}px`);
        element.style.setProperty("--gaze-y", `${gazeCurrent.y.toFixed(2)}px`);
        element.style.setProperty("--blink", blinkAmount.toFixed(3));
        element.style.setProperty("--mouth-open", mouthOpen.toFixed(3));

        if (now - lastDebugUpdate > 250) {
          lastDebugUpdate = now;
          setDebugState({
            blinkCount,
            idleSeconds,
            active: true,
            spatialMode,
            expression: expression?.mood ?? (isSpeakingRef.current ? "speaking" : "idle"),
          });
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
          <div>Avatar Life: {debugState.active ? "ACTIVE" : "PAUSED"}</div>
          <div>Spatial Mode: {debugState.spatialMode}</div>
          <div>Expression: {debugState.expression}</div>
          <div>Blinks: {debugState.blinkCount}</div>
          <div>Idle: {debugState.idleSeconds}s</div>
        </div>
      )}
    </div>
  );
};
