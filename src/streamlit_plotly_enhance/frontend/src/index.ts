import type { FrontendRenderer } from "@streamlit/component-v2-lib";
import Plotly from "plotly.js-dist-min";
import "./style.css";

type SupportedEvent = "click" | "hover" | "unhover" | "relayout";

type ComponentData = {
  figure?: {
    data?: unknown[];
    layout?: Record<string, unknown>;
  };
  events?: SupportedEvent[];
  config?: Record<string, unknown>;
};

const EVENT_TO_PLOTLY_EVENT: Record<SupportedEvent, string> = {
  click: "plotly_click",
  hover: "plotly_hover",
  unhover: "plotly_unhover",
  relayout: "plotly_relayout"
};

const renderer: FrontendRenderer = (component) => {
  const { parentElement, data, setTriggerValue } = component;
  const root = ensureRoot(parentElement);
  const chart = ensureChart(root);
  const componentData = (data ?? {}) as ComponentData;
  const figure = componentData.figure ?? {};
  const events = componentData.events ?? ["click"];
  const config = componentData.config ?? {};

  let disposed = false;

  renderPlot(chart, figure, config)
    .then(() => {
      if (disposed) {
        return;
      }
      console.debug("plotly-cell-events rendered", {
        events,
        hasOn: typeof (chart as { on?: unknown }).on
      });
      for (const event of events) {
        bindEvent(chart, event, (payload) => {
          setTriggerValue("event", payload);
        });
      }
    })
    .catch((error) => {
      showError(root, error);
    });

  return () => {
    disposed = true;
    try {
      Plotly.purge(chart);
    } catch {
      // Ignore cleanup errors from already-purged nodes.
    }
  };
};

async function renderPlot(
  chart: HTMLElement,
  figure: NonNullable<ComponentData["figure"]>,
  config: Record<string, unknown>
) {
  const data = Array.isArray(figure.data) ? figure.data : [];
  const layout = {
    autosize: true,
    ...(isRecord(figure.layout) ? figure.layout : {})
  };
  await Plotly.react(chart, data as Plotly.Data[], layout as Partial<Plotly.Layout>, {
    responsive: true,
    displaylogo: false,
    ...config
  } as Partial<Plotly.Config>);
}

function bindEvent(
  chart: HTMLElement,
  event: SupportedEvent,
  send: (payload: Record<string, unknown>) => void
) {
  const plotlyEvent = EVENT_TO_PLOTLY_EVENT[event];
  const plot = chart as HTMLElement & {
    on?: (eventName: string, handler: (eventData: unknown) => void) => void;
    removeAllListeners?: (eventName: string) => void;
  };

  console.debug("plotly-cell-events bind", {
    event,
    plotlyEvent,
    hasOn: typeof plot.on,
    hasRemoveAllListeners: typeof plot.removeAllListeners
  });
  plot.removeAllListeners?.(plotlyEvent);
  plot.on?.(plotlyEvent, (eventData: unknown) => {
    const payload = sanitizeEvent(event, plotlyEvent, eventData);
    console.debug("plotly-cell-events payload", payload);
    send(payload);
  });
}

function sanitizeEvent(event: string, plotlyEvent: string, eventData: unknown) {
  if (event === "relayout") {
    return {
      event,
      plotly_event: plotlyEvent,
      points: [],
      relayout: jsonSafe(eventData),
      raw: jsonSafe(eventData)
    };
  }

  const raw = isRecord(eventData) ? eventData : {};
  const rawPoints = Array.isArray(raw.points) ? raw.points : [];
  const points = rawPoints.map((point) => sanitizePoint(point));
  return {
    event,
    plotly_event: plotlyEvent,
    points,
    relayout: null,
    raw: null
  };
}

function sanitizePoint(point: unknown) {
  const record = isRecord(point) ? point : {};
  const trace = isRecord(record.data) ? record.data : {};
  return {
    curveNumber: jsonSafe(record.curveNumber),
    pointNumber: jsonSafe(record.pointNumber),
    pointNumbers: jsonSafe(record.pointNumbers),
    x: jsonSafe(record.x),
    y: jsonSafe(record.y),
    z: jsonSafe(record.z),
    customdata: jsonSafe(record.customdata),
    text: jsonSafe(record.text),
    traceType: jsonSafe(trace.type),
    traceName: jsonSafe(trace.name),
    trace: {
      type: jsonSafe(trace.type),
      name: jsonSafe(trace.name),
      z: jsonSafe(trace.z),
      x: jsonSafe(trace.x),
      y: jsonSafe(trace.y)
    }
  };
}

function ensureRoot(parentElement: HTMLElement | ShadowRoot) {
  let root = parentElement.querySelector(".plotly-cell-events-root") as HTMLElement | null;
  if (!root) {
    root = document.createElement("div");
    root.className = "plotly-cell-events-root";
    parentElement.appendChild(root);
  }
  return root;
}

function ensureChart(root: HTMLElement) {
  root.replaceChildren();
  const chart = document.createElement("div");
  chart.className = "plotly-cell-events-chart";
  root.appendChild(chart);
  return chart;
}

function showError(root: HTMLElement, error: unknown) {
  root.replaceChildren();
  const message = error instanceof Error ? error.message : String(error);
  const errorBox = document.createElement("div");
  errorBox.className = "plotly-cell-events-error";
  errorBox.textContent = `Plotly cell events component failed to render: ${message}`;
  root.appendChild(errorBox);
}

function jsonSafe(value: unknown): unknown {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value === "string" || typeof value === "boolean") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item) => jsonSafe(item));
  }
  if (isRecord(value)) {
    const output: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value)) {
      if (typeof item !== "function") {
        output[key] = jsonSafe(item);
      }
    }
    return output;
  }
  return String(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export default renderer;
