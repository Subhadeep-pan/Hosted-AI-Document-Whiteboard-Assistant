import { useState, useRef } from "react";
import { MathJaxContext } from "better-react-mathjax";

import useWhiteboardSocket from "../../hooks/useWhiteboardSocket";
import { solveWhiteboard } from "../../api/whiteboardApi";
import WhiteboardTopBar from "./WhiteboardTopBar";
import WhiteboardToolbar from "./WhiteboardToolbar";
import WhiteboardCanvas from "./WhiteboardCanvas";
import WhiteboardAnswerOverlay from "./WhiteboardAnswerOverlay";


const ANSWER_ROW_HEIGHT = 46;

// FIX: previously <MathJaxContext> used its default config, which
// resolves its CDN script somewhat unpredictably depending on network/
// browser conditions - that's why LaTeX was showing up as raw text
// like "\(t = \frac{...}{...}\)" instead of being typeset. Pinning an
// explicit, reliable CDN URL + config fixes that.
const MATHJAX_CONFIG = {
  loader: { load: ["input/tex", "output/chtml"] },
  tex: { packages: { "[+]": ["ams"] } },
};
const MATHJAX_SRC = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-chtml.js";


function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}


// Computes the bounding box of the strokes drawn
// since the last Run.
function boundingBoxOf(strokes) {
  if (strokes.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const stroke of strokes) {
    for (const point of stroke.points) {
      minX = Math.min(minX, point.x);
      minY = Math.min(minY, point.y);
      maxX = Math.max(maxX, point.x);
      maxY = Math.max(maxY, point.y);
    }
  }

  return {
    minX,
    minY,
    maxX,
    maxY,
  };
}


export default function Whiteboard({
  roomId,
  userName,
  darkMode,
  onLeave,
}) {
  const {
    elements,
    users,
    connected,
    dictOfVars,
    send,
    addElementLocally,
    clearLocally,
    setVar,
  } = useWhiteboardSocket(roomId, userName);


  const canvasRef = useRef(null);

  // Strokes drawn since the last Run.
  const recentStrokesRef = useRef([]);


  const [color, setColor] = useState("#1f2937");
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState("");


  const handleStrokeComplete = (stroke) => {
    recentStrokesRef.current.push(stroke);

    send({
      type: "element_add",
      element: stroke,
    });
  };


  const handleClear = () => {
    clearLocally();

    recentStrokesRef.current = [];

    send({
      type: "clear",
    });
  };


  const handleAnswerDragEnd = (updatedAnswer) => {
    addElementLocally(updatedAnswer);

    send({
      type: "element_update",
      element: updatedAnswer,
    });
  };


  const handleRun = async () => {
    setRunning(true);
    setRunError("");


    try {
      // Make sure the canvas exists.
      if (!canvasRef.current) {
        throw new Error("Whiteboard canvas is not ready.");
      }


      // Convert the current whiteboard to a PNG.
      const imageBase64 = canvasRef.current.toDataURL();


      // Send image + current variables to backend.
      const response = await solveWhiteboard(
        imageBase64,
        dictOfVars
      );


      console.log(
        "Whiteboard solver response:",
        response
      );


      // Backend should return:
      //
      // {
      //   results: [
      //     {
      //       expr: "2 + 3",
      //       result: "5",
      //       latex: "2 + 3 = 5",
      //       assign: false
      //     }
      //   ]
      // }


      if (response?.error) {
        throw new Error(response.error);
      }


      const results = response?.results;


      if (!Array.isArray(results)) {
        throw new Error(
          "AI solver returned an invalid response."
        );
      }


      // Find where the recent drawing is located.
      const bbox = boundingBoxOf(
        recentStrokesRef.current
      );


      // Put the answer beside the drawing.
      const baseX = bbox
        ? bbox.maxX + 24
        : 30;

      const baseY = bbox
        ? bbox.minY
        : 30;


      results.forEach((item, index) => {
        if (!item) {
          return;
        }


        // If Gemini identified a variable assignment,
        // store it for future calculations.
        if (item.assign) {
          setVar(
            item.expr,
            item.result
          );
        }


        const answer = {
          id: uid(),
          type: "answer",

          x: baseX,

          y:
            baseY +
            index * ANSWER_ROW_HEIGHT,

          latex:
            item.latex ||
            `${item.expr} = ${item.result}`,
        };


        // Show answer immediately.
        addElementLocally(answer);


        // Save answer to the shared whiteboard.
        send({
          type: "element_add",
          element: answer,
        });
      });


      // Clear the recent strokes list
      // after successful processing.
      recentStrokesRef.current = [];


    } catch (error) {

      console.error(
        "Whiteboard solver error:",
        error
      );


      // During development, show the actual error.
      setRunError(
        error?.message ||
        "Couldn't reach the AI solver. Try again."
      );


    } finally {
      setRunning(false);
    }
  };


  return (
    <MathJaxContext config={MATHJAX_CONFIG} src={MATHJAX_SRC}>

      <div className="flex flex-col h-screen bg-slate-50 dark:bg-slate-950">

        <WhiteboardTopBar
          roomId={roomId}
          connected={connected}
          users={users}
          onLeave={onLeave}
        />


        <WhiteboardToolbar
          color={color}
          onColorChange={setColor}
          onClear={handleClear}
          onRun={handleRun}
          running={running}
          runError={runError}
          dictOfVars={dictOfVars}
        />


        <WhiteboardCanvas
          ref={canvasRef}
          elements={elements}
          color={color}
          darkMode={darkMode}
          onStrokeComplete={handleStrokeComplete}
        >

          <WhiteboardAnswerOverlay
            elements={elements}
            onDragEnd={handleAnswerDragEnd}
          />

        </WhiteboardCanvas>

      </div>

    </MathJaxContext>
  );
}
