import React, { useEffect } from "react";

const ImageModal = ({ src, alt = "Preview image", onClose }) => {
  useEffect(() => {
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prevOverflow;
    };
  }, []);

  if (!src) return null;

  const handleOverlayMouseDown = (e) => {
    if (e.target === e.currentTarget) onClose?.();
  };

  const handleOverlayKeyDown = (e) => {
    if (e.key === "Escape") onClose?.();
  };

  return (
    <div
      className="image-modal"
      role="dialog"
      aria-modal="true"
      onMouseDown={handleOverlayMouseDown}
      onKeyDown={handleOverlayKeyDown}
      tabIndex={-1}
    >
      <div className="modal-content">
        <button className="close-btn" aria-label="Close" onClick={onClose}>
          ✕
        </button>
        <img className="modal-image" src={src} alt={alt} />
      </div>
    </div>
  );
};

export default ImageModal;

