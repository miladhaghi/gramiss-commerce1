"use client";

import { useState } from "react";
import {
  NetworkError,
  SystemPageChrome,
} from "../components/system-states";

export default function NetworkErrorQaPage() {
  const [loading, setLoading] = useState(false);

  function retryConnectivityCheck() {
    if (loading) return;
    setLoading(true);
    window.setTimeout(() => setLoading(false), 700);
  }

  return (
    <SystemPageChrome>
      <NetworkError
        loading={loading}
        onRetry={retryConnectivityCheck}
      />
    </SystemPageChrome>
  );
}
