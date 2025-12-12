import type { Node, Edge } from "@xyflow/svelte";
import { Position } from "@xyflow/svelte";
import type { TraceSpan } from "../types";
import { hasSpanError, formatDuration } from "../utils";

interface SpanNodeData {
  span: TraceSpan;
  serviceName: string;
  hasError: boolean;
  duration: string;
  isSlowest: boolean;
  isInPath?: boolean;
  isSelected?: boolean;
}

export function createSpanGraph(
  spans: TraceSpan[],
  slowestSpan?: TraceSpan | null
): {
  //@ts-ignore
  nodes: Node<SpanNodeData>[];
  edges: Edge[];
  bounds: { width: number; height: number };
} {
  //@ts-ignore
  const nodes: Node<SpanNodeData>[] = [];
  const edges: Edge[] = [];

  const sortedSpans = [...spans].sort((a, b) => {
    if (a.depth !== b.depth) return a.depth - b.depth;
    return a.span_order - b.span_order;
  });

  const VERTICAL_SPACING = 100;
  const HORIZONTAL_SPACING = 250;

  const depthYPositions = new Map<number, number>();
  let maxX = 0;
  let maxY = 0;

  sortedSpans.forEach((span) => {
    const serviceName = span.service_name;
    const spanHasError = hasSpanError(span);
    const isSlowest = slowestSpan?.span_id === span.span_id;

    const x = span.depth * HORIZONTAL_SPACING;
    let y = depthYPositions.get(span.depth) || 0;

    depthYPositions.set(span.depth, y + VERTICAL_SPACING);

    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);

    nodes.push({
      id: span.span_id,
      type: "span",
      position: { x, y },
      data: {
        span,
        serviceName,
        hasError: spanHasError,
        duration: formatDuration(span.duration_ms),
        isSlowest,
        isInPath: false,
        isSelected: false,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    });

    if (span.parent_span_id) {
      edges.push({
        id: `e-${span.parent_span_id}-${span.span_id}`,
        source: span.parent_span_id,
        target: span.span_id,
        type: "smoothstep",
        animated: true,
        //@ts-ignore
        className: spanHasError ? "error" : "",
        style: spanHasError
          ? "stroke: var(--color-error-600); stroke-width: 1;"
          : "stroke: #000; stroke-width: 1;",
        markerEnd: {
          type: "arrowclosed",
          color: spanHasError ? "#d93025" : "#000",
        },
      });
    }
  });

  const bounds = {
    width: maxX + 300,
    height: maxY + 150,
  };

  return { nodes, edges, bounds };
}

/**
 * Find all nodes in the path (ancestors + descendants) of a clicked node
 */
export function getConnectedPath(nodeId: string, edges: Edge[]): Set<string> {
  const pathNodeIds = new Set<string>([nodeId]);

  // Build adjacency maps
  const childrenMap = new Map<string, string[]>();
  const parentMap = new Map<string, string>();

  edges.forEach((edge) => {
    const parent = edge.source;
    const child = edge.target;

    if (!childrenMap.has(parent)) {
      childrenMap.set(parent, []);
    }
    childrenMap.get(parent)!.push(child);
    parentMap.set(child, parent);
  });

  let currentId = nodeId;
  while (parentMap.has(currentId)) {
    const parentId = parentMap.get(currentId)!;
    pathNodeIds.add(parentId);
    currentId = parentId;
  }

  const queue = [nodeId];
  while (queue.length > 0) {
    const current = queue.shift()!;
    const children = childrenMap.get(current) || [];

    children.forEach((childId) => {
      if (!pathNodeIds.has(childId)) {
        pathNodeIds.add(childId);
        queue.push(childId);
      }
    });
  }

  return pathNodeIds;
}

export function getPathNodeIds(
  nodes: Node[],
  edges: Edge[],
  selectedNodeId: string | null
): Set<string> {
  if (!selectedNodeId) return new Set();

  const childrenMap = new Map<string, Set<string>>();
  const parentsMap = new Map<string, Set<string>>();

  for (const edge of edges) {
    if (!childrenMap.has(edge.source)) childrenMap.set(edge.source, new Set());
    childrenMap.get(edge.source)!.add(edge.target);

    if (!parentsMap.has(edge.target)) parentsMap.set(edge.target, new Set());
    parentsMap.get(edge.target)!.add(edge.source);
  }

  const pathIds = new Set<string>([selectedNodeId]);

  // Upstream traversal (Ancestors)
  const addAncestors = (id: string) => {
    const parents = parentsMap.get(id);
    if (parents) {
      for (const parentId of parents) {
        if (!pathIds.has(parentId)) {
          pathIds.add(parentId);
          addAncestors(parentId);
        }
      }
    }
  };
  addAncestors(selectedNodeId);

  // Downstream traversal (Descendants)
  const addDescendants = (id: string) => {
    const children = childrenMap.get(id);
    if (children) {
      for (const childId of children) {
        if (!pathIds.has(childId)) {
          pathIds.add(childId);
          addDescendants(childId);
        }
      }
    }
  };
  addDescendants(selectedNodeId);

  return pathIds;
}

export function highlightPathNodes(
  nodes: Node[],
  pathNodeIds: Set<string>,
  selectedNodeId: string | null
): Node[] {
  if (!selectedNodeId) {
    return nodes.map((node) => ({
      ...node,
      class: "",
      data: { ...node.data, isInPath: false, isSelected: false },
    }));
  }

  return nodes.map((node) => {
    const isSelected = node.id === selectedNodeId;
    const isInPath = pathNodeIds.has(node.id);

    return {
      ...node,
      class: [isInPath ? "in-path" : "", isSelected ? "selected" : ""]
        .filter(Boolean)
        .join(" "),
      data: {
        ...node.data,
        isSelected,
        isInPath,
      },
    };
  });
}

export function highlightPathEdges(
  edges: Edge[],
  pathNodeIds: Set<string>,
  selectedNodeId: string | null
): Edge[] {
  if (!selectedNodeId) {
    return edges.map((edge) => ({
      ...edge,
      class: edge.data?.isError ? "error" : "",
      animated: true,
    }));
  }

  return edges.map((edge) => {
    const isInPath =
      pathNodeIds.has(edge.source) && pathNodeIds.has(edge.target);
    const isError = edge.data?.isError;

    return {
      ...edge,
      class: [isInPath ? "in-path" : "", isError ? "error" : ""]
        .filter(Boolean)
        .join(" "),
      animated: isInPath,
    };
  });
}
