import {
  useRef,
  useEffect,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from "react";


// The actual drawing surface.
//
// The canvas internal resolution follows the rendered CSS size,
// multiplied by devicePixelRatio so drawing stays sharp.
//
// Coordinates are always stored in CSS-pixel space.
// This keeps mouse/touch coordinates aligned with the drawing.
const WhiteboardCanvas = forwardRef(function WhiteboardCanvas(
  {
    elements,
    color,
    darkMode,
    onStrokeComplete,
    children,
  },
  ref
) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);

  const elementsRef = useRef(elements);

  const drawingRef = useRef(false);
  const currentStrokeRef = useRef(null);


  // Keep the latest elements available to drawing functions.
  useEffect(() => {
    elementsRef.current = elements;
  }, [elements]);


  // Draw all saved strokes onto the canvas.
  const draw = useCallback(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }


    const dpr = window.devicePixelRatio || 1;

    const ctx = canvas.getContext("2d");

    if (!ctx) {
      return;
    }


    // Canvas width/height are physical pixels.
    // Convert them back to CSS pixels.
    const cssWidth = canvas.width / dpr;
    const cssHeight = canvas.height / dpr;


    // Reset transform before clearing.
    ctx.setTransform(
      dpr,
      0,
      0,
      dpr,
      0,
      0
    );


    ctx.clearRect(
      0,
      0,
      cssWidth,
      cssHeight
    );


    // Background.
    ctx.fillStyle = darkMode
      ? "#0f172a"
      : "#ffffff";

    ctx.fillRect(
      0,
      0,
      cssWidth,
      cssHeight
    );


    // Draw every stroke.
    for (const element of elementsRef.current) {

      if (
        element.type !== "stroke" ||
        !Array.isArray(element.points) ||
        element.points.length === 0
      ) {
        continue;
      }


      ctx.strokeStyle =
        element.color || "#1f2937";

      ctx.lineWidth = 3;

      ctx.lineJoin = "round";
      ctx.lineCap = "round";


      ctx.beginPath();


      element.points.forEach(
        (point, index) => {

          if (index === 0) {
            ctx.moveTo(
              point.x,
              point.y
            );
          } else {
            ctx.lineTo(
              point.x,
              point.y
            );
          }

        }
      );


      ctx.stroke();
    }

  }, [darkMode]);


  // Redraw whenever elements change.
  useEffect(() => {
    draw();
  }, [elements, draw]);


  // Resize canvas to exactly match its container.
  useEffect(() => {

    const canvas = canvasRef.current;
    const container = containerRef.current;


    if (!canvas || !container) {
      return;
    }


    const resize = () => {

      const rect =
        container.getBoundingClientRect();

      const dpr =
        window.devicePixelRatio || 1;


      const width = Math.max(
        1,
        Math.floor(rect.width)
      );

      const height = Math.max(
        1,
        Math.floor(rect.height)
      );


      // Physical pixel buffer.
      canvas.width =
        Math.max(
          1,
          Math.floor(width * dpr)
        );

      canvas.height =
        Math.max(
          1,
          Math.floor(height * dpr)
        );


      // CSS display size.
      canvas.style.width =
        `${width}px`;

      canvas.style.height =
        `${height}px`;


      draw();
    };


    const observer =
      new ResizeObserver(resize);


    observer.observe(container);

    resize();


    return () => {
      observer.disconnect();
    };

  }, [draw]);


  // Convert pointer coordinates into
  // whiteboard CSS-pixel coordinates.
  const getPoint = (event) => {

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return {
        x: 0,
        y: 0,
      };
    }


    const rect =
      canvas.getBoundingClientRect();


    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };


  const handlePointerDown = (event) => {

    // Only respond to the primary pointer.
    if (
      event.pointerType === "mouse" &&
      event.button !== 0
    ) {
      return;
    }


    drawingRef.current = true;


    const point =
      getPoint(event);


    currentStrokeRef.current = {
      id:
        Math.random()
          .toString(36)
          .slice(2) +
        Date.now().toString(36),

      type: "stroke",

      color,

      points: [
        point,
      ],
    };


    canvasRef.current?.setPointerCapture(
      event.pointerId
    );
  };


  const handlePointerMove = (event) => {

    if (!drawingRef.current) {
      return;
    }


    const stroke =
      currentStrokeRef.current;


    if (!stroke) {
      return;
    }


    stroke.points.push(
      getPoint(event)
    );


    // Temporarily add/update the current stroke
    // locally while drawing.
    elementsRef.current = [
      ...elementsRef.current.filter(
        (element) =>
          element.id !== stroke.id
      ),

      {
        ...stroke,
      },
    ];


    draw();
  };


  const finishDrawing = () => {

    if (!drawingRef.current) {
      return;
    }


    drawingRef.current = false;


    const stroke =
      currentStrokeRef.current;


    if (
      stroke &&
      stroke.points.length > 1
    ) {
      onStrokeComplete(stroke);
    }


    currentStrokeRef.current = null;
  };


  const handlePointerUp = (event) => {

    try {
      canvasRef.current?.releasePointerCapture(
        event.pointerId
      );
    } catch {
      // Pointer capture may already be released.
    }


    finishDrawing();
  };


  const handlePointerCancel = () => {
    finishDrawing();
  };


  // Expose canvas.toDataURL() to Whiteboard.jsx.
  useImperativeHandle(
    ref,
    () => ({
      toDataURL: () => {

        if (!canvasRef.current) {
          return "";
        }

        return canvasRef.current.toDataURL(
          "image/png"
        );
      },
    }),
    []
  );


  return (
    <div
      ref={containerRef}
      className="relative flex-1 overflow-hidden"
    >

      <canvas
        ref={canvasRef}
        className="touch-none cursor-crosshair block"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerCancel}
        onPointerLeave={handlePointerUp}
      />


      {children}

    </div>
  );
});


export default WhiteboardCanvas;