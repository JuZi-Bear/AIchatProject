import { currentApiBaseUrl, currentApiMode } from "./client";
import { normalizeRunEvent } from "./events";

import type { RunEvent } from "@/types/runEvent";

export type RunEventSubscription = {
  supported: boolean;
  close: () => void;
};

export function subscribeRunEvents(
  platformRunId: string,
  onMessage: (event: RunEvent) => void,
  onError?: (error: Error) => void,
  onOpen?: () => void,
): RunEventSubscription {
  if (currentApiMode !== "java") {
    onError?.(new Error("Python Direct 模式不支持实时事件流，请使用历史事件查询"));
    return {
      supported: false,
      close: () => undefined,
    };
  }

  if (!platformRunId) {
    onError?.(new Error("缺少 platformRunId，无法订阅实时事件"));
    return {
      supported: false,
      close: () => undefined,
    };
  }

  const baseUrl = currentApiBaseUrl.replace(/\/$/, "");
  const url = `${baseUrl}/platform/runs/${encodeURIComponent(platformRunId)}/events/stream`;
  const source = new EventSource(url);

  source.addEventListener("open", () => {
    onOpen?.();
  });

  source.addEventListener("connected", () => {
    onOpen?.();
  });

  source.addEventListener("run-event", (event) => {
    const parsed = parseRunEvent((event as MessageEvent<string>).data);
    if (parsed) {
      onMessage(parsed);
    }
  });

  source.addEventListener("stream-error", (event) => {
    const message = parseErrorMessage((event as MessageEvent<string>).data);
    onError?.(new Error(message));
  });

  source.addEventListener("final", () => {
    source.close();
  });

  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      return;
    }

    onError?.(new Error("SSE 实时事件流连接异常"));
  };

  return {
    supported: true,
    close: () => source.close(),
  };
}

function parseRunEvent(data: string) {
  try {
    return normalizeRunEvent(JSON.parse(data));
  } catch {
    return null;
  }
}

function parseErrorMessage(data: string) {
  try {
    const parsed = JSON.parse(data) as { message?: string };
    return parsed.message || "SSE 实时事件流返回错误";
  } catch {
    return data || "SSE 实时事件流返回错误";
  }
}
