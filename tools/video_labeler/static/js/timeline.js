/**
 * KTTC_FC Video Labeler - Interactive HTML5 Canvas Timeline
 * Handles multi-track timeline rendering, time ruler, step blocks (B1..B9, B0),
 * keyframe stars, warning borders, draggable playhead, and zoom/pan.
 */

class TimelineController {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {Object} options
   */
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.container = canvas.parentElement;

    this.duration = 0; // Video duration in seconds
    this.currentTime = 0; // Current playhead time in seconds
    this.fps = 30.0;
    this.zoom = 1.0; // Zoom factor 1.0 to 10.0

    this.events = {}; // { stepKey: { start_sec, key_sec, end_sec } }
    this.activeStep = "B1";
    this.hoverTime = null;

    this.isDragging = false;
    this.onSeek = options.onSeek || (() => {});
    this.onSeekStart = options.onSeekStart || (() => {});
    this.onSeekMove = options.onSeekMove || options.onSeek || (() => {});
    this.onSeekEnd = options.onSeekEnd || options.onSeek || (() => {});
    this.onHover = options.onHover || (() => {});
    this.onSelectStep = options.onSelectStep || (() => {});

    this.needsRender = false;
    this.rafId = null;
    this.onAnimationFrame = this.onAnimationFrame.bind(this);

    // Step color palette matching the HTML standard & guide_data.js
    this.stepColors = {
      "B1": "#2563eb",
      "B2": "#dc2626",
      "B3": "#d97706",
      "B4": "#059669",
      "B5": "#0891b2",
      "B6a": "#7c3aed",
      "B6_clean": "#7c3aed",
      "B6b": "#c026d3",
      "B6_cut": "#c026d3",
      "B7": "#ea580c",
      "B8": "#4f46e5",
      "B9": "#16a34a",
      "B0": "#475569"
    };

    this.init();
  }

  init() {
    this.bindEvents();
    this.resize();
  }

  bindEvents() {
    if (!this.canvas) return;

    // Mouse seek & drag
    this.canvas.addEventListener("mousedown", (e) => this.handleMouseDown(e));
    this.canvas.addEventListener("mousemove", (e) => this.handleMouseMove(e));
    this.canvas.addEventListener("mouseleave", () => this.handleMouseLeave());

    // Window mouse events for smooth dragging outside canvas
    if (typeof window !== "undefined") {
      window.addEventListener("mousemove", (e) => {
        if (this.isDragging) {
          this.handleDrag(e);
        }
      });

      window.addEventListener("mouseup", (e) => {
        this.handleMouseUp(e);
      });

      // Handle container resize
      window.addEventListener("resize", () => this.resize());
    }
  }

  requestRender() {
    this.needsRender = true;
    if (!this.rafId) {
      if (typeof requestAnimationFrame !== "undefined") {
        this.rafId = requestAnimationFrame(this.onAnimationFrame);
      } else {
        this.needsRender = false;
        this.render();
      }
    }
  }

  onAnimationFrame() {
    this.rafId = null;
    if (this.needsRender) {
      this.needsRender = false;
      this.render();
    }
  }

  handleMouseUp(e) {
    if (this.isDragging) {
      this.isDragging = false;
      this.onSeekEnd(this.currentTime);
      this.requestRender();
    }
  }

  resize() {
    if (!this.canvas || !this.container) return;

    const baseWidth = Math.max(300, this.container.clientWidth);
    const totalWidth = Math.round(baseWidth * this.zoom);

    const dpr = (typeof window !== "undefined" && window.devicePixelRatio) || 1;
    this.canvas.width = Math.round(totalWidth * dpr);
    this.canvas.height = Math.round(104 * dpr);

    this.canvas.style.width = `${totalWidth}px`;
    this.canvas.style.height = "104px";

    this.ctx.setTransform(1, 0, 0, 1, 0, 0); // reset transform
    this.ctx.scale(dpr, dpr);

    this.requestRender();
  }

  setDuration(duration) {
    this.duration = Math.max(0, Number(duration) || 0);
    this.requestRender();
  }

  setFps(fps) {
    this.fps = Math.max(1, Number(fps) || 30.0);
    this.requestRender();
  }

  setCurrentTime(time) {
    this.currentTime = Math.max(0, Math.min(this.duration, Number(time) || 0));
    this.requestRender();

    // Auto-scroll container if playhead goes out of view when zoomed
    if (this.zoom > 1.0 && this.container) {
      const x = this.timeToX(this.currentTime);
      const scrollLeft = this.container.scrollLeft;
      const clientWidth = this.container.clientWidth;
      const margin = 50;

      if (x < scrollLeft + margin) {
        this.container.scrollLeft = Math.max(0, x - margin);
      } else if (x > scrollLeft + clientWidth - margin) {
        this.container.scrollLeft = x - clientWidth + margin;
      }
    }
  }

  setEvents(eventsMap, activeStep) {
    this.events = eventsMap ? JSON.parse(JSON.stringify(eventsMap)) : {};
    if (activeStep) {
      this.activeStep = activeStep;
    }
    this.requestRender();
  }

  setActiveStep(activeStep) {
    this.activeStep = activeStep;
    this.requestRender();
  }

  setZoom(zoom) {
    this.zoom = Math.max(1.0, Math.min(10.0, Number(zoom) || 1.0));
    if (this.container) {
      this.container.style.overflowX = this.zoom > 1.0 ? "auto" : "hidden";
    }
    this.resize();
  }

  getVirtualWidth() {
    const baseWidth = Math.max(300, this.container ? this.container.clientWidth : 800);
    return Math.round(baseWidth * this.zoom);
  }

  timeToX(time) {
    if (!this.duration || this.duration <= 0) return 0;
    const width = this.getVirtualWidth();
    return (time / this.duration) * width;
  }

  xToTime(x) {
    if (!this.duration || this.duration <= 0) return 0;
    const width = this.getVirtualWidth();
    return (x / width) * this.duration;
  }

  handleMouseDown(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = Math.max(0, Math.min(this.duration, this.xToTime(x)));

    this.isDragging = true;
    this.currentTime = t;

    // Check if clicked directly inside a step block to select that step
    const clickedStep = this.getStepAtX(x);
    if (clickedStep && clickedStep !== this.activeStep) {
      this.onSelectStep(clickedStep);
    }

    this.onSeekStart(t);
    this.requestRender();
  }

  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = Math.max(0, Math.min(this.duration, this.xToTime(x)));

    this.hoverTime = t;
    this.onHover(t);

    if (this.isDragging) {
      this.currentTime = t;
      this.onSeekMove(t);
    }

    this.requestRender();
  }

  handleDrag(e) {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = Math.max(0, Math.min(this.duration, this.xToTime(x)));

    this.hoverTime = t;
    this.onHover(t);
    if (this.isDragging) {
      this.currentTime = t;
      this.onSeekMove(t);
    }
    this.requestRender();
  }

  handleMouseLeave() {
    if (!this.isDragging) {
      this.hoverTime = null;
      this.requestRender();
    }
  }

  getStepAtX(x) {
    if (!this.events) return null;
    for (const [step, data] of Object.entries(this.events)) {
      if (!data) continue;
      const s = Number(data.start_sec);
      const e = Number(data.end_sec);
      if (s !== null && e !== null && !isNaN(s) && !isNaN(e) && s < e) {
        const x1 = this.timeToX(s);
        const x2 = this.timeToX(e);
        if (x >= x1 && x <= x2) {
          return step;
        }
      }
    }
    return null;
  }

  /**
   * Main Render Loop
   */
  render() {
    const ctx = this.ctx;
    const width = this.getVirtualWidth();
    const height = 104;

    if (!ctx) return;

    // Clear Canvas
    ctx.clearRect(0, 0, width, height);

    // 1. Draw Background
    ctx.fillStyle = "#060911";
    ctx.fillRect(0, 0, width, height);

    // 2. Draw Time Ruler (y: 0 -> 24)
    this.drawTimeRuler(ctx, width);

    // 3. Draw Auto-filled B0 (Idle / Transition) Gaps (y: 26 -> 98)
    this.drawB0Gaps(ctx, width);

    // 4. Draw Marked Step Blocks (B1..B9)
    this.drawStepBlocks(ctx, width);

    // 5. Draw Hover Indicator Line (if hovering and not dragging)
    if (this.hoverTime !== null) {
      const hoverX = this.timeToX(this.hoverTime);
      ctx.save();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.35)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(hoverX, 0);
      ctx.lineTo(hoverX, height);
      ctx.stroke();
      ctx.restore();
    }

    // 6. Draw Current Video Playhead (Red Line & Pointer)
    this.drawPlayhead(ctx);
  }

  /**
   * Draw Top Time Ruler with seconds & tick marks
   */
  drawTimeRuler(ctx, width) {
    const rulerHeight = 24;

    // Ruler background
    ctx.fillStyle = "#0d1322";
    ctx.fillRect(0, 0, width, rulerHeight);

    // Ruler bottom border
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, rulerHeight);
    ctx.lineTo(width, rulerHeight);
    ctx.stroke();

    if (!this.duration || this.duration <= 0) return;

    const pps = width / this.duration; // pixels per second

    // Determine interval for major ticks based on zoom / pps
    let majorSec = 5;
    let minorSec = 1;

    if (pps >= 120) {
      majorSec = 1;
      minorSec = 0.2;
    } else if (pps >= 50) {
      majorSec = 1;
      minorSec = 0.5;
    } else if (pps >= 20) {
      majorSec = 2;
      minorSec = 1;
    } else if (pps >= 8) {
      majorSec = 5;
      minorSec = 1;
    } else if (pps >= 3) {
      majorSec = 10;
      minorSec = 2;
    } else {
      majorSec = 30;
      minorSec = 10;
    }

    // Draw minor ticks
    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let t = 0; t <= this.duration; t += minorSec) {
      const x = (t / this.duration) * width;
      ctx.moveTo(x, rulerHeight - 4);
      ctx.lineTo(x, rulerHeight);
    }
    ctx.stroke();

    // Draw major ticks & labels
    ctx.strokeStyle = "#64748b";
    ctx.fillStyle = "#94a3b8";
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    ctx.beginPath();
    for (let t = 0; t <= this.duration; t += majorSec) {
      const x = (t / this.duration) * width;
      ctx.moveTo(x, rulerHeight - 8);
      ctx.lineTo(x, rulerHeight);

      // Time string mm:ss
      const m = Math.floor(t / 60);
      const s = Math.floor(t % 60);
      const timeStr = `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;

      // Avoid drawing label too close to edges
      if (x > 15 && x < width - 15) {
        ctx.fillText(timeStr, x, 4);
      }
    }
    ctx.stroke();
  }

  /**
   * Compute B0 (idle / transition) gap intervals
   * @param {Array<{start: number, end: number}>} activeIntervals
   * @param {number} duration
   * @returns {Array<{start: number, end: number}>}
   */
  static computeB0Gaps(activeIntervals, duration) {
    if (!duration || duration <= 0) return [];
    if (!activeIntervals || !Array.isArray(activeIntervals)) return [];

    const validIntervals = activeIntervals
      .filter((iv) => iv && typeof iv.start === "number" && typeof iv.end === "number" && !isNaN(iv.start) && !isNaN(iv.end) && iv.start < iv.end)
      .map((iv) => ({ start: iv.start, end: iv.end }));

    // Sort by start time
    validIntervals.sort((a, b) => a.start - b.start);

    const gaps = [];
    let curr = 0.0;
    const minGap = 0.05; // 50ms min gap

    for (const interval of validIntervals) {
      if (interval.start - curr > minGap) {
        gaps.push({ start: Number(curr.toFixed(3)), end: Number(interval.start.toFixed(3)) });
      }
      curr = Math.max(curr, interval.end);
    }

    if (duration - curr > minGap) {
      gaps.push({ start: Number(curr.toFixed(3)), end: Number(duration.toFixed(3)) });
    }

    return gaps;
  }

  computeB0Gaps(activeIntervals, duration) {
    const d = duration !== undefined ? duration : (this && this.duration ? this.duration : 0);
    return TimelineController.computeB0Gaps(activeIntervals, d);
  }

  /**
   * Auto-fill B0 (idle / transition) blocks for all gaps
   */
  drawB0Gaps(ctx, width) {
    if (!this.duration || this.duration <= 0) return;

    // Collect all active steps with valid start and end
    const activeIntervals = [];
    for (const [step, data] of Object.entries(this.events)) {
      if (step === "B0" || !data) continue;
      const s = Number(data.start_sec);
      const e = Number(data.end_sec);
      if (s !== null && e !== null && !isNaN(s) && !isNaN(e) && s < e) {
        activeIntervals.push({ start: s, end: e });
      }
    }

    const gaps = this.computeB0Gaps(activeIntervals, this.duration);

    // Render B0 gap blocks
    const trackY = 28;
    const trackH = 68;

    ctx.save();
    for (const gap of gaps) {
      const x1 = this.timeToX(gap.start);
      const x2 = this.timeToX(gap.end);
      const w = Math.max(1, x2 - x1);

      // Background
      ctx.fillStyle = "rgba(30, 41, 59, 0.45)";
      this.drawRoundedRect(ctx, x1, trackY, w, trackH, 4, true, false);

      // Dashed border
      ctx.strokeStyle = "rgba(71, 85, 105, 0.35)";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      this.drawRoundedRect(ctx, x1, trackY, w, trackH, 4, false, true);

      // Label B0 if width allows
      if (w > 26) {
        ctx.fillStyle = "#64748b";
        ctx.font = "bold 9px 'Plus Jakarta Sans', sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("B0", x1 + w / 2, trackY + trackH / 2);
      }
    }
    ctx.restore();
  }

  /**
   * Draw Marked Action Step Blocks (B1..B9)
   */
  drawStepBlocks(ctx, width) {
    if (!this.events) return;

    const trackY = 28;
    const trackH = 68;

    for (const [step, data] of Object.entries(this.events)) {
      if (!data) continue;

      const s = data.start_sec !== null && data.start_sec !== undefined ? Number(data.start_sec) : null;
      const k = data.key_sec !== null && data.key_sec !== undefined ? Number(data.key_sec) : null;
      const e = data.end_sec !== null && data.end_sec !== undefined ? Number(data.end_sec) : null;

      // Skip if nothing marked yet
      if (s === null && k === null && e === null) continue;

      const isCurrentStep = step === this.activeStep;
      const baseColor = this.stepColors[step] || "#3b82f6";

      // If only single points exist (partial)
      if (s !== null && (e === null || isNaN(e))) {
        // Draw start flag line
        const xStart = this.timeToX(s);
        ctx.save();
        ctx.strokeStyle = "#10b981";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(xStart, trackY);
        ctx.lineTo(xStart, trackY + trackH);
        ctx.stroke();

        ctx.fillStyle = "#10b981";
        ctx.font = "bold 10px 'Plus Jakarta Sans', sans-serif";
        ctx.textAlign = "left";
        ctx.fillText(`${step} [S]`, xStart + 3, trackY + 12);
        ctx.restore();
        continue;
      }

      // If full interval exists
      if (s !== null && e !== null && !isNaN(s) && !isNaN(e)) {
        const x1 = this.timeToX(s);
        const x2 = this.timeToX(e);
        const blockW = Math.max(4, x2 - x1);

        // Validation checks
        const isTimingValid = e > s && k !== null && !isNaN(k) && k > s && k < e;

        ctx.save();

        // 1. Block Background
        if (!isTimingValid) {
          // Warning red background for invalid step
          ctx.fillStyle = "rgba(239, 68, 68, 0.25)";
        } else {
          // Color block with gradient
          const grad = ctx.createLinearGradient(x1, trackY, x1, trackY + trackH);
          grad.addColorStop(0, this.hexToRgba(baseColor, 0.85));
          grad.addColorStop(1, this.hexToRgba(baseColor, 0.65));
          ctx.fillStyle = grad;
        }
        this.drawRoundedRect(ctx, x1, trackY, blockW, trackH, 4, true, false);

        // 2. Block Border
        if (!isTimingValid) {
          // Red warning border with dashed lines
          ctx.strokeStyle = "#ef4444";
          ctx.lineWidth = 2;
          ctx.setLineDash([4, 2]);
          this.drawRoundedRect(ctx, x1, trackY, blockW, trackH, 4, false, true);
        } else if (isCurrentStep) {
          // Active step highlight: thick white outline + outer glow
          ctx.shadowColor = baseColor;
          ctx.shadowBlur = 10;
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2;
          this.drawRoundedRect(ctx, x1, trackY, blockW, trackH, 4, false, true);
        } else {
          // Normal step border
          ctx.strokeStyle = this.hexToRgba(baseColor, 0.9);
          ctx.lineWidth = 1;
          this.drawRoundedRect(ctx, x1, trackY, blockW, trackH, 4, false, true);
        }

        // 3. Step Label & Badges
        ctx.shadowBlur = 0; // reset glow
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 11px 'Plus Jakarta Sans', sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "top";

        let labelText = step;
        if (!isTimingValid) {
          labelText = `⚠️ ${step}`;
        }

        if (blockW > 28) {
          ctx.fillText(labelText, x1 + 6, trackY + 6);
        }

        // Duration text inside block if enough space
        if (blockW > 70 && e > s) {
          ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
          ctx.font = "9px 'JetBrains Mono', monospace";
          ctx.fillText(`${(e - s).toFixed(2)}s`, x1 + 6, trackY + 22);
        }

        // 4. Draw Start & End Edge Markers
        ctx.fillStyle = "#10b981"; // Green start marker
        ctx.fillRect(x1, trackY, 2.5, trackH);

        ctx.fillStyle = "#f43f5e"; // Rose end marker
        ctx.fillRect(x2 - 2.5, trackY, 2.5, trackH);

        // 5. Draw Golden Keyframe Star Indicator at key_sec
        if (k !== null && !isNaN(k)) {
          const xKey = this.timeToX(k);

          // Vertical key line
          ctx.strokeStyle = "#fbbf24";
          ctx.lineWidth = 1.5;
          ctx.setLineDash([2, 2]);
          ctx.beginPath();
          ctx.moveTo(xKey, trackY);
          ctx.lineTo(xKey, trackY + trackH);
          ctx.stroke();
          ctx.setLineDash([]); // clear dash

          // Golden Star
          this.drawStar(ctx, xKey, trackY + trackH / 2, 5, 8, 4, "#fbbf24", "#b45309");
        }

        ctx.restore();
      }
    }
  }

  /**
   * Draw Draggable Red Playhead Line & Top Triangle Handle
   */
  drawPlayhead(ctx) {
    if (!this.duration || this.duration <= 0) return;

    const x = this.timeToX(this.currentTime);
    const height = 104;

    ctx.save();

    // Top Triangle Pointer in ruler
    ctx.fillStyle = "#ef4444";
    ctx.beginPath();
    ctx.moveTo(x - 5, 0);
    ctx.lineTo(x + 5, 0);
    ctx.lineTo(x, 10);
    ctx.closePath();
    ctx.fill();

    // Vertical Playhead Line
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 2;
    ctx.shadowColor = "rgba(239, 68, 68, 0.7)";
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();

    ctx.restore();
  }

  /**
   * Helper to draw a 5-point polygon star
   */
  drawStar(ctx, cx, cy, spikes = 5, outerRadius = 8, innerRadius = 4, fillStyle = "#fbbf24", strokeStyle = "#b45309") {
    let rot = (Math.PI / 2) * 3;
    let x = cx;
    let y = cy;
    const step = Math.PI / spikes;

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy - outerRadius);

    for (let i = 0; i < spikes; i++) {
      x = cx + Math.cos(rot) * outerRadius;
      y = cy + Math.sin(rot) * outerRadius;
      ctx.lineTo(x, y);
      rot += step;

      x = cx + Math.cos(rot) * innerRadius;
      y = cy + Math.sin(rot) * innerRadius;
      ctx.lineTo(x, y);
      rot += step;
    }

    ctx.lineTo(cx, cy - outerRadius);
    ctx.closePath();

    if (fillStyle) {
      ctx.fillStyle = fillStyle;
      ctx.shadowColor = "rgba(245, 158, 11, 0.8)";
      ctx.shadowBlur = 8;
      ctx.fill();
    }

    if (strokeStyle) {
      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.restore();
  }

  /**
   * Helper to draw a rounded rectangle
   */
  drawRoundedRect(ctx, x, y, width, height, radius, fill = true, stroke = false) {
    if (width <= 0 || height <= 0) return;
    radius = Math.min(radius, width / 2, height / 2);

    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();

    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
  }

  /**
   * Helper to convert HEX to RGBA string
   */
  hexToRgba(hex, alpha = 1.0) {
    hex = hex.replace("#", "");
    if (hex.length === 3) {
      hex = hex.split("").map((c) => c + c).join("");
    }
    const num = parseInt(hex, 16);
    const r = (num >> 16) & 255;
    const g = (num >> 8) & 255;
    const b = num & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
}

// Support Node.js / Jest environments
if (typeof module !== "undefined" && module.exports) {
  module.exports = { TimelineController };
}

// Support Browser globals
if (typeof window !== "undefined") {
  window.TimelineController = TimelineController;
}
