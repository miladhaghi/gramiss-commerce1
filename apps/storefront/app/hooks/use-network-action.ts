"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type NetworkActionStatus = "ready" | "loading" | "error";

function shouldFail(scope: string) {
  if (typeof window === "undefined") return false;
  if (!window.navigator.onLine) return true;

  const queryValue =
    new URLSearchParams(window.location.search).get("network-error") ?? "";
  if (
    queryValue === "1" ||
    queryValue === "all" ||
    queryValue.split(",").includes(scope)
  ) {
    return true;
  }

  try {
    const stored = window.localStorage.getItem("gramiss:simulate-network-error");
    return Boolean(
      stored === "1" ||
        stored === "all" ||
        stored?.split(",").includes(scope),
    );
  } catch {
    return false;
  }
}

export function useNetworkAction(scope: string) {
  const [status, setStatus] = useState<NetworkActionStatus>("ready");
  const lastAction = useRef<() => void>(() => undefined);
  const timerRef = useRef<number | null>(null);

  const attempt = useCallback(
    (action: () => void, delay = 420) => {
      lastAction.current = action;
      setStatus("loading");
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
      timerRef.current = window.setTimeout(() => {
        timerRef.current = null;
        if (shouldFail(scope)) {
          setStatus("error");
          return;
        }
        setStatus("ready");
        action();
      }, delay);
    },
    [scope],
  );

  const retry = useCallback(() => {
    attempt(lastAction.current);
  }, [attempt]);

  const checkInitialLoad = useCallback(
    (onSuccess: () => void = () => undefined) => {
      if (!shouldFail(scope)) return;
      attempt(onSuccess);
    },
    [attempt, scope],
  );

  useEffect(
    () => () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    },
    [],
  );

  return {
    status,
    attempt,
    retry,
    checkInitialLoad,
    dismiss: () => setStatus("ready"),
  };
}
