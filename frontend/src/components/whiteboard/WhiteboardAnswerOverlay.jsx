import { useRef } from "react";
import { MathJax } from "better-react-mathjax";
import { FaGripVertical } from "react-icons/fa";

// Renders every "answer" element as a draggable HTML card.
// MathJax is used because answers contain LaTeX.
export default function WhiteboardAnswerOverlay({
  elements,
  onDragEnd,
}) {
  const answers = elements.filter(
    (el) => el.type === "answer"
  );

  return (
    <>
      {answers.map((answer) => (
        <AnswerCard
          key={answer.id}
          answer={answer}
          onDragEnd={onDragEnd}
        />
      ))}
    </>
  );
}


function AnswerCard({
  answer,
  onDragEnd,
}) {
  const cardRef = useRef(null);
  const draggingRef = useRef(false);

  const offsetRef = useRef({
    x: 0,
    y: 0,
  });


  const handlePointerDown = (event) => {
    if (!cardRef.current) {
      return;
    }

    draggingRef.current = true;

    const rect =
      cardRef.current.getBoundingClientRect();

    offsetRef.current = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };

    cardRef.current.setPointerCapture(
      event.pointerId
    );
  };


  const handlePointerMove = (event) => {
    if (!draggingRef.current) {
      return;
    }

    if (!cardRef.current) {
      return;
    }

    const parent =
      cardRef.current.offsetParent;

    if (!parent) {
      return;
    }

    const parentRect =
      parent.getBoundingClientRect();

    const x =
      event.clientX -
      parentRect.left -
      offsetRef.current.x;

    const y =
      event.clientY -
      parentRect.top -
      offsetRef.current.y;

    cardRef.current.style.left =
      `${x}px`;

    cardRef.current.style.top =
      `${y}px`;
  };


  const handlePointerUp = () => {
    if (!draggingRef.current) {
      return;
    }

    draggingRef.current = false;

    if (!cardRef.current) {
      return;
    }

    const x = parseFloat(
      cardRef.current.style.left
    );

    const y = parseFloat(
      cardRef.current.style.top
    );

    onDragEnd({
      ...answer,
      x,
      y,
    });
  };


  const latex =
    answer.latex ||
    `${answer.expr || ""} = ${answer.result || ""}`;


  return (
    <div
      ref={cardRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      style={{
        left: answer.x,
        top: answer.y,
      }}
      className="absolute max-w-xs rounded-xl border border-accent-200 dark:border-accent-700/50 bg-white/95 dark:bg-slate-800/95 shadow-md px-3 py-2 text-sm cursor-grab active:cursor-grabbing select-none"
    >
      <div className="flex items-start gap-2">

        <FaGripVertical
          className="text-slate-300 mt-1 shrink-0"
          size={10}
        />

        <div className="text-slate-800 dark:text-slate-100">
          <MathJax dynamic>
            {`\\(${latex}\\)`}
          </MathJax>
        </div>

      </div>
    </div>
  );
}