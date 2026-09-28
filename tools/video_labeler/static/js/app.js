/**
 * KTTC_FC Video Labeler & Slicer - Application Controller
 * Manages playlist, HTML5 video player, 3-point marking (S-K-E),
 * dynamic guideline companion, auto-save, timeline synchronization,
 * hotkey shortcuts, and FFmpeg video slicing.
 */

class AppController {
  constructor() {
    this.currentFolder = "VIDEO_TRAIN";
    this.videos = [];
    this.filteredVideos = [];
    this.currentVideo = null;
    this.currentVideoIndex = -1;
    this.videoInfo = { fps: 30.0, duration_sec: 0, total_frames: 0, width: 0, height: 0 };

    this.activeStep = "B1";
    this.eventsByStep = {
      "B1": null,
      "B2": null,
      "B3": null,
      "B4": null,
      "B5": null,
      "B6a": null,
      "B6b": null,
      "B7": null,
      "B8": null,
      "B9": null
    };

    this.statusFilter = "all";
    this.searchQuery = "";
    this.isDirty = false;
    this.autoSaveTimer = null;
    this.sliceJobId = null;
    this.slicePollInterval = null;

    // Auto-advance step state (persisted in localStorage, default: true)
    this.isAutoAdvanceEnabled = typeof localStorage !== "undefined"
      ? localStorage.getItem("kttc_auto_advance") !== "false"
      : true;
    this.autoAdvanceTimer = null;

    // Decoupled Seek Queue state
    this.isSeeking = false;
    this.pendingSeekTime = null;
    this.wasPlayingBeforeDrag = false;
    this.wasMutedBeforeDrag = false;

    this.initElements();
    this.initTimeline();
    this.bindEvents();
    this.initAutoSave();
    this.applyInitialPanelState();

    // Initial load
    this.loadPlaylist(this.currentFolder);
    this.updateGuidePanel(this.activeStep);
  }

  /**
   * Cache all DOM element references
   */
  initElements() {
    // Top Bar
    this.headerVideoTitle = document.getElementById("headerVideoTitle");
    this.headerVideoMeta = document.getElementById("headerVideoMeta");
    this.saveStatusIndicator = document.getElementById("saveStatusIndicator");
    this.btnOpenHelp = document.getElementById("btnOpenHelp");

    // Left Panel - Playlist & Filter
    this.folderInput = document.getElementById("folderInput");
    this.btnConfirmFolder = document.getElementById("btnConfirmFolder");
    this.btnLoadFolder = document.getElementById("btnLoadFolder");
    this.progressStatsText = document.getElementById("progressStatsText");
    this.batchProgressBar = document.getElementById("batchProgressBar");
    this.videoSearchInput = document.getElementById("videoSearchInput");
    this.filterTabs = document.querySelectorAll(".filter-tab");
    this.videoList = document.getElementById("videoList");

    // Center Panel - Video Player
    this.videoPlayer = document.getElementById("videoPlayer");
    this.currentVideoTitle = document.getElementById("currentVideoTitle");
    this.videoStatusBadge = document.getElementById("videoStatusBadge");
    this.videoResBadge = document.getElementById("videoResBadge");
    this.fpsDisplay = document.getElementById("fpsDisplay");
    this.overlayVideoName = document.getElementById("overlayVideoName");
    this.timeDisplay = document.getElementById("timeDisplay");
    this.frameDisplay = document.getElementById("frameDisplay");
    this.videoEmptyPrompt = document.getElementById("videoEmptyPrompt");

    // Player Transport Controls
    this.btnBack1s = document.getElementById("btnBack1s");
    this.btnPrevFrame = document.getElementById("btnPrevFrame");
    this.btnPlayPause = document.getElementById("btnPlayPause");
    this.playIcon = document.getElementById("playIcon");
    this.playText = document.getElementById("playText");
    this.btnNextFrame = document.getElementById("btnNextFrame");
    this.btnFwd1s = document.getElementById("btnFwd1s");
    this.speedBtns = document.querySelectorAll(".speed-btn");
    this.btnMute = document.getElementById("btnMute");
    this.volumeSlider = document.getElementById("volumeSlider");

    // Step Navigation Pills
    this.stepPills = document.querySelectorAll(".step-pill");

    // 3-Point Action Buttons & Readout
    this.btnSetStart = document.getElementById("btnSetStart");
    this.btnSetKey = document.getElementById("btnSetKey");
    this.btnSetEnd = document.getElementById("btnSetEnd");
    this.btnClearStep = document.getElementById("btnClearStep");
    this.btnSetStartSub = document.getElementById("btnSetStartSub");
    this.btnSetKeySub = document.getElementById("btnSetKeySub");
    this.btnSetEndSub = document.getElementById("btnSetEndSub");

    this.curStepLabel = document.getElementById("curStepLabel");
    this.curStepStart = document.getElementById("curStepStart");
    this.curStepKey = document.getElementById("curStepKey");
    this.curStepEnd = document.getElementById("curStepEnd");
    this.curStepDuration = document.getElementById("curStepDuration");
    this.stepValidationAlert = document.getElementById("stepValidationAlert");
    this.stepValidationMsg = document.getElementById("stepValidationMsg");

    // Auto-advance toggle
    this.chkAutoAdvance = document.getElementById("chkAutoAdvance");
    if (this.chkAutoAdvance) {
      this.chkAutoAdvance.checked = this.isAutoAdvanceEnabled;
      this.chkAutoAdvance.addEventListener("change", (e) => {
        this.isAutoAdvanceEnabled = e.target.checked;
        if (typeof localStorage !== "undefined") {
          try {
            localStorage.setItem("kttc_auto_advance", String(this.isAutoAdvanceEnabled));
          } catch (_) {}
        }
        this.showToast(
          this.isAutoAdvanceEnabled ? "Đã BẬT tự động chuyển bước (Auto Next)" : "Đã TẮT tự động chuyển bước (Auto Next)",
          "⚡"
        );
      });
    }

    // Center Panel Quick Guidance Strip
    this.curStepQuickGuide = document.getElementById("curStepQuickGuide");
    this.curStepQuickTool = document.getElementById("curStepQuickTool");
    this.curStepGuideS = document.getElementById("curStepGuideS");
    this.curStepGuideKey = document.getElementById("curStepGuideKey");
    this.curStepGuideE = document.getElementById("curStepGuideE");

    // Timeline Controls & Canvas
    this.cursorTimeDisplay = document.getElementById("cursorTimeDisplay");
    this.timelineZoom = document.getElementById("timelineZoom");
    this.btnZoomIn = document.getElementById("btnZoomIn");
    this.btnZoomOut = document.getElementById("btnZoomOut");
    this.btnZoomFit = document.getElementById("btnZoomFit");
    this.timelineCanvas = document.getElementById("timelineCanvas");

    // Bottom Action Bar
    this.btnSaveAnnotation = document.getElementById("btnSaveAnnotation");
    this.btnOpenSliceModal = document.getElementById("btnOpenSliceModal");
    this.btnPrevVideo = document.getElementById("btnPrevVideo");
    this.btnNextVideo = document.getElementById("btnNextVideo");

    // Right Panel - Dynamic Guideline Companion
    this.guideStepDuration = document.getElementById("guideStepDuration");
    this.guideStepTitle = document.getElementById("guideStepTitle");
    this.guideSampleRange = document.getElementById("guideSampleRange");
    this.guideMomentS = document.getElementById("guideMomentS");
    this.guideMomentKey = document.getElementById("guideMomentKey");
    this.guideMomentE = document.getElementById("guideMomentE");
    this.guideImgStart = document.getElementById("guideImgStart");
    this.guideCaptionStart = document.getElementById("guideCaptionStart");
    this.guideImgKey = document.getElementById("guideImgKey");
    this.guideCaptionKey = document.getElementById("guideCaptionKey");
    this.guideImgEnd = document.getElementById("guideImgEnd");
    this.guideCaptionEnd = document.getElementById("guideCaptionEnd");
    this.guideToolName = document.getElementById("guideToolName");
    this.guideToolDetail = document.getElementById("guideToolDetail");
    this.guideCriteria = document.getElementById("guideCriteria");
    this.guideWarning = document.getElementById("guideWarning");

    // Slicing Modal
    this.sliceModal = document.getElementById("sliceModal");
    this.btnCloseSliceModal = document.getElementById("btnCloseSliceModal");
    this.btnCancelSlice = document.getElementById("btnCancelSlice");
    this.btnConfirmSlice = document.getElementById("btnConfirmSlice");
    this.chkFastCopy = document.getElementById("chkFastCopy");
    this.chkSliceB0 = document.getElementById("chkSliceB0");
    this.sliceProgressContainer = document.getElementById("sliceProgressContainer");
    this.sliceStatusMsg = document.getElementById("sliceStatusMsg");
    this.sliceProgressPct = document.getElementById("sliceProgressPct");
    this.sliceProgressBar = document.getElementById("sliceProgressBar");
    this.sliceClipsList = document.getElementById("sliceClipsList");

    // Help Modal
    this.helpModal = document.getElementById("helpModal");
    this.btnCloseHelpModal = document.getElementById("btnCloseHelpModal");
    this.btnDismissHelp = document.getElementById("btnDismissHelp");

    // Toast
    this.toastNotification = document.getElementById("toastNotification");
    this.toastIcon = document.getElementById("toastIcon");
    this.toastMessage = document.getElementById("toastMessage");

    // Collapsible Sidebars (Left Playlist & Right Handbook)
    this.leftSidebar = document.getElementById("leftSidebar");
    this.guideCompanionPanel = document.getElementById("guideCompanionPanel");
    this.btnToggleLeftPanel = document.getElementById("btnToggleLeftPanel");
    this.btnToggleRightPanel = document.getElementById("btnToggleRightPanel");
    this.btnCollapseLeft = document.getElementById("btnCollapseLeft");
    this.btnCollapseRight = document.getElementById("btnCollapseRight");
    this.btnExpandLeft = document.getElementById("btnExpandLeft");
    this.btnExpandRight = document.getElementById("btnExpandRight");

    // Load persisted collapse state from localStorage
    this.isLeftCollapsed = typeof localStorage !== "undefined" && localStorage.getItem("kttc_left_collapsed") === "true";
    this.isRightCollapsed = typeof localStorage !== "undefined" && localStorage.getItem("kttc_right_collapsed") === "true";

    // Decoupled Seek Queue state
    this.isSeeking = false;
    this.pendingSeekTime = null;
    this.wasPlayingBeforeDrag = false;
    this.wasMutedBeforeDrag = false;
  }

  /**
   * Initialize Timeline Controller
   */
  initTimeline() {
    if (!this.timelineCanvas) return;

    this.timeline = new TimelineController(this.timelineCanvas, {
      onSeekStart: (time) => this.handleSeekStart(time),
      onSeekMove: (time) => this.handleSeekMove(time),
      onSeekEnd: (time) => this.handleSeekEnd(time),
      onSeek: (time) => {
        this.handleSeekMove(time);
        this.handleSeekEnd(time);
      },
      onHover: (time) => {
        if (this.cursorTimeDisplay) {
          this.cursorTimeDisplay.textContent = `Con trỏ: ${this.formatTime(time)}`;
        }
      },
      onSelectStep: (step) => {
        this.setActiveStep(step);
      }
    });
  }

  /**
   * Bind all event listeners
   */
  bindEvents() {
    // Folder loading
    this.btnConfirmFolder?.addEventListener("click", () => {
      this.currentFolder = this.folderInput.value.trim() || "VIDEO_TRAIN";
      this.loadPlaylist(this.currentFolder);
    });

    this.btnLoadFolder?.addEventListener("click", () => {
      this.currentFolder = this.folderInput.value.trim() || "VIDEO_TRAIN";
      this.loadPlaylist(this.currentFolder);
    });

    this.folderInput?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        this.currentFolder = this.folderInput.value.trim() || "VIDEO_TRAIN";
        this.loadPlaylist(this.currentFolder);
      }
    });

    // Playlist Search & Filter
    this.videoSearchInput?.addEventListener("input", (e) => {
      this.searchQuery = e.target.value.toLowerCase().trim();
      this.filterAndRenderPlaylist();
    });

    this.filterTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        this.filterTabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        this.statusFilter = tab.dataset.filter || "all";
        this.filterAndRenderPlaylist();
      });
    });

    // Video Player events
    this.videoPlayer?.addEventListener("timeupdate", () => {
      if (!this.timeline || !this.timeline.isDragging) {
        this.updateHUD();
        this.timeline?.setCurrentTime(this.videoPlayer.currentTime);
      }
    });

    this.videoPlayer?.addEventListener("play", () => this.updatePlayPauseButton());
    this.videoPlayer?.addEventListener("pause", () => this.updatePlayPauseButton());
    this.videoPlayer?.addEventListener("ended", () => this.updatePlayPauseButton());
    this.videoPlayer?.addEventListener("seeked", () => this.handleVideoSeeked());

    // Transport buttons
    this.btnPlayPause?.addEventListener("click", () => this.togglePlayPause());
    this.btnPrevFrame?.addEventListener("click", () => this.stepFrame(-1));
    this.btnNextFrame?.addEventListener("click", () => this.stepFrame(1));
    this.btnBack1s?.addEventListener("click", () => this.stepSeconds(-1.0));
    this.btnFwd1s?.addEventListener("click", () => this.stepSeconds(1.0));

    // Playback Speed buttons
    this.speedBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const speed = parseFloat(btn.dataset.speed) || 1.0;
        this.setPlaybackSpeed(speed);
      });
    });

    // Volume & Mute
    this.btnMute?.addEventListener("click", () => this.toggleMute());
    this.volumeSlider?.addEventListener("input", (e) => {
      if (this.videoPlayer) {
        this.videoPlayer.volume = parseFloat(e.target.value);
        this.videoPlayer.muted = false;
        if (this.btnMute) this.btnMute.textContent = this.videoPlayer.volume === 0 ? "🔇" : "🔊";
      }
    });

    // Step Navigation Pills
    this.stepPills.forEach((pill) => {
      pill.addEventListener("click", () => {
        const step = pill.dataset.step;
        if (step) {
          this.setActiveStep(step);
        }
      });
    });

    // 3-Point Action Buttons
    this.btnSetStart?.addEventListener("click", () => this.setMark("start"));
    this.btnSetKey?.addEventListener("click", () => this.setMark("key"));
    this.btnSetEnd?.addEventListener("click", () => this.setMark("end"));
    this.btnClearStep?.addEventListener("click", () => this.clearActiveStep());

    // Timeline Zoom controls
    this.timelineZoom?.addEventListener("input", (e) => {
      const zoom = parseFloat(e.target.value) || 1.0;
      this.timeline?.setZoom(zoom);
    });

    this.btnZoomIn?.addEventListener("click", () => {
      const cur = parseFloat(this.timelineZoom.value) || 1.0;
      const next = Math.min(10.0, cur + 0.5);
      this.timelineZoom.value = next;
      this.timeline?.setZoom(next);
    });

    this.btnZoomOut?.addEventListener("click", () => {
      const cur = parseFloat(this.timelineZoom.value) || 1.0;
      const next = Math.max(1.0, cur - 0.5);
      this.timelineZoom.value = next;
      this.timeline?.setZoom(next);
    });

    this.btnZoomFit?.addEventListener("click", () => {
      this.timelineZoom.value = 1.0;
      this.timeline?.setZoom(1.0);
    });

    // Bottom Action Buttons
    this.btnSaveAnnotation?.addEventListener("click", () => this.saveAnnotation());
    this.btnOpenSliceModal?.addEventListener("click", () => this.openSliceModal());
    this.btnPrevVideo?.addEventListener("click", () => this.switchVideoRelative(-1));
    this.btnNextVideo?.addEventListener("click", () => this.switchVideoRelative(1));

    // Modals
    this.btnOpenHelp?.addEventListener("click", () => this.openHelpModal());
    this.btnCloseHelpModal?.addEventListener("click", () => this.closeHelpModal());
    this.btnDismissHelp?.addEventListener("click", () => this.closeHelpModal());

    this.btnCloseSliceModal?.addEventListener("click", () => this.closeSliceModal());
    this.btnCancelSlice?.addEventListener("click", () => this.closeSliceModal());
    this.btnConfirmSlice?.addEventListener("click", () => this.startSlicing());

    // Collapsible Sidebar Toggles
    this.btnToggleLeftPanel?.addEventListener("click", () => this.toggleLeftPanel());
    this.btnCollapseLeft?.addEventListener("click", () => this.toggleLeftPanel(true));
    this.btnExpandLeft?.addEventListener("click", () => this.toggleLeftPanel(false));

    this.btnToggleRightPanel?.addEventListener("click", () => this.toggleRightPanel());
    this.btnCollapseRight?.addEventListener("click", () => this.toggleRightPanel(true));
    this.btnExpandRight?.addEventListener("click", () => this.toggleRightPanel(false));

    // Global Keyboard Shortcuts
    window.addEventListener("keydown", (e) => this.handleGlobalKeyDown(e));
  }

  /**
   * Apply persisted sidebar visibility states on application launch
   */
  applyInitialPanelState() {
    if (this.isLeftCollapsed) {
      this.toggleLeftPanel(true, false);
    }
    if (this.isRightCollapsed) {
      this.toggleRightPanel(true, false);
    }
  }

  /**
   * Toggle Left Playlist Sidebar (expand / collapse)
   */
  toggleLeftPanel(forceCollapse = null, save = true) {
    if (!this.leftSidebar) return;
    const shouldCollapse = forceCollapse !== null ? forceCollapse : !this.leftSidebar.classList.contains("hidden");

    if (shouldCollapse) {
      this.leftSidebar.classList.add("hidden");
      this.btnExpandLeft?.classList.remove("hidden");
      this.btnToggleLeftPanel?.classList.add("bg-slate-700", "text-sky-400");
    } else {
      this.leftSidebar.classList.remove("hidden");
      this.btnExpandLeft?.classList.add("hidden");
      this.btnToggleLeftPanel?.classList.remove("bg-slate-700", "text-sky-400");
    }

    this.isLeftCollapsed = shouldCollapse;
    if (save && typeof localStorage !== "undefined") {
      try {
        localStorage.setItem("kttc_left_collapsed", shouldCollapse ? "true" : "false");
      } catch (_) {}
    }

    // Recalibrate timeline canvas width when viewport changes
    if (typeof requestAnimationFrame !== "undefined") {
      requestAnimationFrame(() => this.timeline?.resize());
    } else {
      this.timeline?.resize();
    }
  }

  /**
   * Toggle Right Guideline Companion Sidebar (expand / collapse)
   */
  toggleRightPanel(forceCollapse = null, save = true) {
    if (!this.guideCompanionPanel) return;
    const shouldCollapse = forceCollapse !== null ? forceCollapse : !this.guideCompanionPanel.classList.contains("hidden");

    if (shouldCollapse) {
      this.guideCompanionPanel.classList.add("hidden");
      this.btnExpandRight?.classList.remove("hidden");
      this.btnToggleRightPanel?.classList.add("bg-slate-700", "text-amber-400");
    } else {
      this.guideCompanionPanel.classList.remove("hidden");
      this.btnExpandRight?.classList.add("hidden");
      this.btnToggleRightPanel?.classList.remove("bg-slate-700", "text-amber-400");
    }

    this.isRightCollapsed = shouldCollapse;
    if (save && typeof localStorage !== "undefined") {
      try {
        localStorage.setItem("kttc_right_collapsed", shouldCollapse ? "true" : "false");
      } catch (_) {}
    }

    // Recalibrate timeline canvas width when viewport changes
    if (typeof requestAnimationFrame !== "undefined") {
      requestAnimationFrame(() => this.timeline?.resize());
    } else {
      this.timeline?.resize();
    }
  }

  /**
   * Load Video Playlist from Backend REST API
   */
  async loadPlaylist(folder) {
    if (this.videoList) {
      this.videoList.innerHTML = `<div class="p-6 text-center text-xs text-slate-500 italic">Đang tải danh sách video từ "${folder}"...</div>`;
    }

    try {
      const res = await fetch(`/api/videos?folder=${encodeURIComponent(folder)}`);
      if (!res.ok) {
        throw new Error(`Không thể tải thư mục (HTTP ${res.status})`);
      }
      const data = await res.json();
      this.videos = data.videos || [];
      this.filterAndRenderPlaylist();
      this.updateProgressStats();

      // If videos found and none selected yet, select first video
      if (this.videos.length > 0 && !this.currentVideo) {
        this.selectVideo(this.videos[0]);
      }
    } catch (err) {
      if (this.videoList) {
        this.videoList.innerHTML = `<div class="p-6 text-center text-xs text-rose-400">❌ Lỗi: ${err.message}</div>`;
      }
      this.showToast(`Lỗi tải playlist: ${err.message}`, "❌");
    }
  }

  /**
   * Filter videos and render Left Panel list
   */
  filterAndRenderPlaylist() {
    this.filteredVideos = this.videos.filter((v) => {
      // Filter by search query
      if (this.searchQuery && !v.name.toLowerCase().includes(this.searchQuery)) {
        return false;
      }
      // Filter by status tab
      if (this.statusFilter !== "all" && v.status !== this.statusFilter) {
        return false;
      }
      return true;
    });

    this.renderPlaylist();
  }

  /**
   * Render HTML for video items in Playlist
   */
  renderPlaylist() {
    if (!this.videoList) return;

    if (this.filteredVideos.length === 0) {
      this.videoList.innerHTML = `<div class="p-6 text-center text-xs text-slate-500 italic">Không tìm thấy video phù hợp</div>`;
      return;
    }

    this.videoList.innerHTML = "";
    this.filteredVideos.forEach((video) => {
      const isActive = this.currentVideo && this.currentVideo.rel_path === video.rel_path;
      const item = document.createElement("div");
      item.className = `video-item p-2.5 cursor-pointer flex items-center justify-between text-xs select-none ${
        isActive ? "active" : ""
      }`;

      // Status badge styling
      let badgeClass = "badge-status-not_annotated";
      let statusText = "Chưa gán";
      if (video.status === "annotated") {
        badgeClass = "badge-status-annotated";
        statusText = "Đã xong";
      } else if (video.status === "in_progress") {
        badgeClass = "badge-status-in_progress";
        statusText = "Đang gán";
      }

      const sizeMB = (video.size_bytes / (1024 * 1024)).toFixed(1);

      item.innerHTML = `
        <div class="min-w-0 flex-1 pr-2">
          <div class="font-bold text-slate-200 truncate ${isActive ? "text-sky-400" : ""}">${video.name}</div>
          <div class="text-[10px] text-slate-500 font-mono mt-0.5">${sizeMB} MB</div>
        </div>
        <span class="${badgeClass} px-2 py-0.5 text-[9px] font-bold rounded-full uppercase tracking-wider shrink-0">
          ${statusText}
        </span>
      `;

      item.addEventListener("click", () => this.selectVideo(video));
      this.videoList.appendChild(item);
    });
  }

  /**
   * Update Progress Stats in Left Panel
   */
  updateProgressStats() {
    const total = this.videos.length;
    const completed = this.videos.filter((v) => v.status === "annotated").length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

    if (this.progressStatsText) {
      this.progressStatsText.textContent = `${completed} / ${total} (${pct}%)`;
    }
    if (this.batchProgressBar) {
      this.batchProgressBar.style.width = `${pct}%`;
    }
  }

  /**
   * Select and load a video
   */
  async selectVideo(video) {
    if (!video) return;

    // Check if previous video had unsaved changes, save to local draft
    if (this.isDirty && this.currentVideo) {
      this.saveLocalDraft();
    }

    this.currentVideo = video;
    this.currentVideoIndex = this.videos.findIndex((v) => v.rel_path === video.rel_path);

    // Update Header & Center Titles
    if (this.headerVideoTitle) this.headerVideoTitle.textContent = video.name;
    if (this.currentVideoTitle) this.currentVideoTitle.textContent = video.name;
    if (this.overlayVideoName) this.overlayVideoName.textContent = video.name;
    if (this.videoEmptyPrompt) this.videoEmptyPrompt.classList.add("hidden");

    this.updateVideoStatusBadge(video.status);
    this.renderPlaylist();

    // Reset in-memory annotations
    this.resetEvents();

    // Fetch video metadata (fps, duration, resolution)
    try {
      const res = await fetch(`/api/video_info?path=${encodeURIComponent(video.rel_path)}`);
      if (res.ok) {
        this.videoInfo = await res.json();
      } else {
        this.videoInfo = { fps: 30.0, duration_sec: 0, total_frames: 0, width: 1920, height: 1080 };
      }
    } catch {
      this.videoInfo = { fps: 30.0, duration_sec: 0, total_frames: 0, width: 1920, height: 1080 };
    }

    // Update video specs badges
    if (this.fpsDisplay) this.fpsDisplay.textContent = `${this.videoInfo.fps.toFixed(1)} FPS`;
    if (this.videoResBadge) this.videoResBadge.textContent = `${this.videoInfo.width} x ${this.videoInfo.height}`;
    if (this.headerVideoMeta) {
      this.headerVideoMeta.textContent = `${this.videoInfo.width}x${this.videoInfo.height} • ${this.videoInfo.fps.toFixed(1)} FPS`;
    }

    // Setup Video Player
    if (this.videoPlayer) {
      this.videoPlayer.src = `/api/stream_video?path=${encodeURIComponent(video.rel_path)}`;
      this.videoPlayer.load();
      this.videoPlayer.currentTime = 0;
    }

    // Configure Timeline
    if (this.timeline) {
      this.timeline.setDuration(this.videoInfo.duration_sec);
      this.timeline.setFps(this.videoInfo.fps);
      this.timeline.setCurrentTime(0);
    }

    // Load Annotation (Remote JSON or Local Draft)
    await this.loadAnnotation(video);

    this.isDirty = false;
    this.updateSaveStatus("Đã đồng bộ");
    this.updateStepReadout();
    this.updateStepDots();
  }

  /**
   * Reset events map for fresh video
   */
  resetEvents() {
    this.eventsByStep = {
      "B1": null,
      "B2": null,
      "B3": null,
      "B4": null,
      "B5": null,
      "B6a": null,
      "B6b": null,
      "B7": null,
      "B8": null,
      "B9": null
    };
  }

  /**
   * Load Annotation from Backend API or Local Draft
   */
  async loadAnnotation(video) {
    // 1. Try local draft first
    const draftKey = `kttc_draft_${video.rel_path}`;
    const localDraft = localStorage.getItem(draftKey);

    let loaded = false;

    // 2. Fetch server annotation
    try {
      const res = await fetch(`/api/annotation?path=${encodeURIComponent(video.rel_path)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "ok" && data.annotation && Array.isArray(data.annotation.events)) {
          // Parse events
          data.annotation.events.forEach((ev) => {
            let label = ev.label;
            if (label === "B6_clean") label = "B6a";
            if (label === "B6_cut") label = "B6b";

            if (this.eventsByStep.hasOwnProperty(label)) {
              this.eventsByStep[label] = {
                start_sec: ev.start_sec !== undefined ? Number(ev.start_sec) : null,
                key_sec: ev.key_sec !== undefined ? Number(ev.key_sec) : null,
                end_sec: ev.end_sec !== undefined ? Number(ev.end_sec) : null
              };
            }
          });
          loaded = true;
        }
      }
    } catch (err) {
      console.warn("Could not fetch remote annotation:", err);
    }

    // 3. Fallback to local draft if remote had no annotation
    if (!loaded && localDraft) {
      try {
        const parsed = JSON.parse(localDraft);
        if (parsed.events) {
          this.eventsByStep = parsed.events;
          this.isDirty = true;
          this.updateSaveStatus("Bản nháp cục bộ");
        }
      } catch (err) {
        console.error("Failed to parse local draft:", err);
      }
    }

    // Sync with timeline
    if (this.timeline) {
      this.timeline.setEvents(this.eventsByStep, this.activeStep);
    }
  }

  /**
   * Update HUD video time & frame display
   */
  updateHUD(explicitTime = null) {
    if (!this.videoPlayer) return;

    const curTime = (explicitTime !== null && explicitTime !== undefined)
      ? Math.max(0, Number(explicitTime) || 0)
      : (this.videoPlayer.currentTime || 0);
    const durTime = this.videoInfo.duration_sec || this.videoPlayer.duration || 0;
    const fps = this.videoInfo.fps || 30.0;

    const curFrame = Math.floor(curTime * fps);
    const totalFrames = this.videoInfo.total_frames || Math.floor(durTime * fps);

    if (this.timeDisplay) {
      this.timeDisplay.textContent = `${this.formatTime(curTime)} / ${this.formatTime(durTime)}`;
    }
    if (this.frameDisplay) {
      this.frameDisplay.textContent = `Frame ${curFrame} / ${totalFrames}`;
    }
  }

  /**
   * Play / Pause toggle
   */
  togglePlayPause() {
    if (!this.videoPlayer) return;
    if (this.videoPlayer.paused) {
      this.videoPlayer.play();
    } else {
      this.videoPlayer.pause();
    }
    this.updatePlayPauseButton();
  }

  updatePlayPauseButton() {
    if (!this.videoPlayer) return;
    const isPlaying = !this.videoPlayer.paused;
    if (this.playIcon) this.playIcon.textContent = isPlaying ? "❚❚" : "▶";
    if (this.playText) this.playText.textContent = isPlaying ? "Tạm dừng" : "Phát";
  }

  /**
   * Step backward or forward by 1 frame
   */
  stepFrame(direction = 1) {
    if (!this.videoPlayer) return;
    this.videoPlayer.pause();

    const fps = this.videoInfo.fps || 30.0;
    const frameDur = 1 / fps;
    const dur = this.videoInfo.duration_sec || this.videoPlayer.duration || 0;

    const newTime = Math.max(0, Math.min(dur, this.videoPlayer.currentTime + direction * frameDur));
    this.videoPlayer.currentTime = newTime;
    this.updateHUD();
    this.timeline?.setCurrentTime(newTime);
  }

  /**
   * Step backward or forward by seconds
   */
  stepSeconds(deltaSec = 1.0) {
    if (!this.videoPlayer) return;
    const dur = this.videoInfo.duration_sec || this.videoPlayer.duration || 0;
    const newTime = Math.max(0, Math.min(dur, this.videoPlayer.currentTime + deltaSec));
    this.videoPlayer.currentTime = newTime;
    this.updateHUD();
    this.timeline?.setCurrentTime(newTime);
  }

  /**
   * Set Playback Speed
   */
  setPlaybackSpeed(speed) {
    if (this.videoPlayer) {
      this.videoPlayer.playbackRate = speed;
    }
    this.speedBtns.forEach((btn) => {
      const s = parseFloat(btn.dataset.speed);
      btn.classList.toggle("active", s === speed);
    });
  }

  /**
   * Toggle Mute
   */
  toggleMute() {
    if (!this.videoPlayer) return;
    this.videoPlayer.muted = !this.videoPlayer.muted;
    if (this.btnMute) {
      this.btnMute.textContent = this.videoPlayer.muted ? "🔇" : "🔊";
    }
  }

  /**
   * Decoupled Seek Queue & Fast-Seek Scrubbing
   */
  handleSeekStart(time) {
    if (!this.videoPlayer) return;
    this.wasPlayingBeforeDrag = !this.videoPlayer.paused;
    if (this.wasPlayingBeforeDrag) {
      this.videoPlayer.pause();
    }
    this.wasMutedBeforeDrag = this.videoPlayer.muted;
    this.videoPlayer.muted = true;
    this.dispatchVideoSeek(time, true);
  }

  handleSeekMove(time) {
    if (!this.videoPlayer) return;
    this.updateHUD(time);
    this.dispatchVideoSeek(time, true);
  }

  handleSeekEnd(time) {
    if (!this.videoPlayer) return;
    this.dispatchVideoSeek(time, false);
    this.videoPlayer.muted = this.wasMutedBeforeDrag;
    if (this.wasPlayingBeforeDrag) {
      const playPromise = this.videoPlayer.play();
      if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch(() => {});
      }
    }
  }

  dispatchVideoSeek(time, isFast = true) {
    if (!this.videoPlayer) return;
    const target = Math.max(0, Number(time) || 0);

    if (this.isSeeking) {
      this.pendingSeekTime = { time: target, isFast };
      return;
    }

    this.isSeeking = true;
    if (isFast && typeof this.videoPlayer.fastSeek === "function") {
      this.videoPlayer.fastSeek(target);
    } else {
      this.videoPlayer.currentTime = target;
    }
  }

  handleVideoSeeked() {
    this.isSeeking = false;
    if (this.pendingSeekTime !== null) {
      const { time, isFast } = this.pendingSeekTime;
      this.pendingSeekTime = null;
      this.dispatchVideoSeek(time, isFast);
    } else {
      this.updateHUD();
    }
  }

  /**
   * Switch Active Step (B1..B9, B0)
   */
  setActiveStep(step) {
    if (step === "B0") {
      this.showToast("B0 là khoảng nghỉ được tự động điền trong các khoảng trống.", "ℹ️");
      return;
    }

    if (this.autoAdvanceTimer) {
      clearTimeout(this.autoAdvanceTimer);
      this.autoAdvanceTimer = null;
    }

    this.activeStep = step;

    // Update step pills UI
    this.stepPills.forEach((pill) => {
      pill.classList.toggle("active", pill.dataset.step === step);
    });

    // Update Right Panel Guide
    this.updateGuidePanel(step);

    // Update Readout & Timeline
    this.updateStepReadout();
    this.timeline?.setActiveStep(step);
  }

  /**
   * Check if a step has all 3 valid marks: start < key < end
   */
  isStepCompleted(step) {
    const data = this.eventsByStep[step];
    if (!data) return false;
    const { start_sec, key_sec, end_sec } = data;
    return (
      start_sec !== null &&
      key_sec !== null &&
      end_sec !== null &&
      end_sec > start_sec &&
      key_sec > start_sec &&
      key_sec < end_sec
    );
  }

  /**
   * Automatically advance to next step in sequence if enabled
   */
  triggerAutoAdvance(currentStep) {
    if (!this.isAutoAdvanceEnabled) return;

    const steps = ["B1", "B2", "B3", "B4", "B5", "B6a", "B6b", "B7", "B8", "B9"];
    const idx = steps.indexOf(currentStep);
    if (idx === -1) return;

    if (this.autoAdvanceTimer) {
      clearTimeout(this.autoAdvanceTimer);
      this.autoAdvanceTimer = null;
    }

    if (idx < steps.length - 1) {
      const nextStep = steps[idx + 1];
      this.showToast(`[${currentStep}] Đã gán xong! ➔ Tự động chuyển sang ${nextStep}...`, "⚡");
      this.autoAdvanceTimer = setTimeout(() => {
        this.autoAdvanceTimer = null;
        this.setActiveStep(nextStep);
      }, 450);
    } else {
      this.showToast(`🎉 Đã hoàn thành bước cuối cùng (${currentStep})!`, "✅");
    }
  }

  /**
   * Set 3-Point Mark: 'start', 'key', 'end'
   */
  setMark(type) {
    if (!this.currentVideo || !this.videoPlayer) {
      this.showToast("Vui lòng chọn video trước khi đặt mốc!", "⚠️");
      return;
    }

    const t = Math.round(this.videoPlayer.currentTime * 1000) / 1000;
    const step = this.activeStep;

    const wasCompleted = this.isStepCompleted(step);

    if (!this.eventsByStep[step]) {
      this.eventsByStep[step] = { start_sec: null, key_sec: null, end_sec: null };
    }

    if (type === "start") {
      this.eventsByStep[step].start_sec = t;
      this.showToast(`[${step}] Đã đặt START: ${this.formatTime(t)}`, "🟢");
    } else if (type === "key") {
      this.eventsByStep[step].key_sec = t;
      this.showToast(`[${step}] Đã đặt KEY_TIME: ${this.formatTime(t)}`, "⭐");
    } else if (type === "end") {
      this.eventsByStep[step].end_sec = t;
      this.showToast(`[${step}] Đã đặt END: ${this.formatTime(t)}`, "🔴");
    }

    this.isDirty = true;
    this.updateSaveStatus("Chưa lưu");
    this.updateStepReadout();
    this.updateStepDots();
    this.timeline?.setEvents(this.eventsByStep, this.activeStep);

    // Auto-advance to next step if enabled & step is now complete:
    // 1) Step transitioned from incomplete to complete (e.g. 3rd mark set)
    // 2) OR user explicitly re-marked 'end' on an already complete step
    const isNowCompleted = this.isStepCompleted(step);
    if (this.isAutoAdvanceEnabled && isNowCompleted) {
      if (!wasCompleted || type === "end") {
        this.triggerAutoAdvance(step);
      }
    }
  }

  /**
   * Clear active step marks
   */
  clearActiveStep() {
    const step = this.activeStep;
    if (this.eventsByStep[step]) {
      this.eventsByStep[step] = null;
      this.isDirty = true;
      this.updateSaveStatus("Chưa lưu");
      this.updateStepReadout();
      this.updateStepDots();
      this.timeline?.setEvents(this.eventsByStep, this.activeStep);
      this.showToast(`Đã xóa mốc của bước ${step}`, "🗑️");
    }
  }

  /**
   * Update Step Readout Box & Validation Alert
   */
  updateStepReadout() {
    const step = this.activeStep;
    const data = this.eventsByStep[step];

    const guide = window.getGuideStep ? window.getGuideStep(step) : null;
    const stepName = guide ? `${guide.step_num}: ${guide.name}` : step;

    if (this.curStepLabel) this.curStepLabel.textContent = stepName;

    const s = data ? data.start_sec : null;
    const k = data ? data.key_sec : null;
    const e = data ? data.end_sec : null;

    if (this.curStepStart) this.curStepStart.textContent = s !== null ? this.formatTime(s) : "--:--.---";
    if (this.curStepKey) this.curStepKey.textContent = k !== null ? this.formatTime(k) : "--:--.---";
    if (this.curStepEnd) this.curStepEnd.textContent = e !== null ? this.formatTime(e) : "--:--.---";

    let durText = "-- s";
    if (s !== null && e !== null && e > s) {
      durText = `${(e - s).toFixed(3)} s`;
    }
    if (this.curStepDuration) this.curStepDuration.textContent = durText;

    // Validation Alert check
    if (this.stepValidationAlert && this.stepValidationMsg) {
      let errorMsg = null;

      if (s !== null && e !== null) {
        if (e <= s) {
          errorMsg = "Mốc thời gian không hợp lệ: START phải nhỏ hơn END.";
        } else if (k !== null && (k <= s || k >= e)) {
          errorMsg = "Mốc then chốt KEY_TIME phải nằm giữa khoảng (START, END) và không được trùng mốc.";
        }
      }

      if (errorMsg) {
        this.stepValidationMsg.textContent = errorMsg;
        this.stepValidationAlert.classList.remove("hidden");
      } else {
        this.stepValidationAlert.classList.add("hidden");
      }
    }
  }

  /**
   * Update Status Dots in Step Pills
   */
  updateStepDots() {
    this.stepPills.forEach((pill) => {
      const step = pill.dataset.step;
      const dot = pill.querySelector(".step-dot");
      if (!dot || !step) return;

      dot.className = "step-dot";
      const data = this.eventsByStep[step];

      if (!data || (data.start_sec === null && data.key_sec === null && data.end_sec === null)) {
        dot.classList.add("empty");
      } else if (
        data.start_sec !== null &&
        data.end_sec !== null &&
        data.key_sec !== null &&
        data.end_sec > data.start_sec &&
        data.key_sec > data.start_sec &&
        data.key_sec < data.end_sec
      ) {
        dot.classList.add("completed");
      } else {
        dot.classList.add("partial");
      }
    });
  }

  /**
   * Update Dynamic Guideline Companion (Right Panel) & Center Quick Guide Strip
   */
  updateGuidePanel(stepId) {
    const guide = window.getGuideStep ? window.getGuideStep(stepId) : null;
    if (!guide) return;

    if (this.guideStepDuration) this.guideStepDuration.textContent = guide.duration || "";
    if (this.guideStepTitle) this.guideStepTitle.textContent = `${guide.step_num}: ${guide.name}`;
    if (this.guideSampleRange) this.guideSampleRange.textContent = guide.sample_range || "";

    // 1. Right Panel 3 Moments Specification
    if (guide.moments) {
      if (this.guideMomentS) this.guideMomentS.textContent = guide.moments.S || "";
      if (this.guideMomentKey) this.guideMomentKey.textContent = guide.moments.Key || "";
      if (this.guideMomentE) this.guideMomentE.textContent = guide.moments.E || "";
    }

    // 2. Center Panel Quick Guidance Strip
    if (this.curStepQuickTool) {
      this.curStepQuickTool.textContent = guide.tool_name ? `🔧 ${guide.tool_name}` : "🔧 Thao tác";
    }
    if (guide.moments) {
      if (this.curStepGuideS) this.curStepGuideS.textContent = guide.moments.S || "";
      if (this.curStepGuideKey) this.curStepGuideKey.textContent = guide.moments.Key || "";
      if (this.curStepGuideE) this.curStepGuideE.textContent = guide.moments.E || "";
    }

    // 3. Action Buttons Subtext Hints (Cleaned & concise)
    if (guide.moments) {
      const getShortHint = (txt) => {
        if (!txt) return "";
        let clean = txt.replace(/^(kho\u1ea3nh kh\u1eafc|k\u1ef9 thu\u1eadt vi\u00ean|ktv)\s*/gi, "").trim();
        clean = clean.replace(/^(kho\u1ea3nh kh\u1eafc|k\u1ef9 thu\u1eadt vi\u00ean|ktv)\s*/gi, "").trim();
        return clean.charAt(0).toUpperCase() + clean.slice(1);
      };

      if (this.btnSetStartSub) {
        const hint = getShortHint(guide.moments.S);
        this.btnSetStartSub.innerHTML = `${hint} <kbd class="kbd-badge ml-1 text-emerald-950 bg-emerald-200 border-emerald-400">S</kbd>`;
      }
      if (this.btnSetKeySub) {
        const hint = getShortHint(guide.moments.Key);
        this.btnSetKeySub.innerHTML = `${hint} <kbd class="kbd-badge ml-1 text-amber-950 bg-amber-200 border-amber-400">K</kbd>`;
      }
      if (this.btnSetEndSub) {
        const hint = getShortHint(guide.moments.E);
        this.btnSetEndSub.innerHTML = `${hint} <kbd class="kbd-badge ml-1 text-rose-950 bg-rose-200 border-rose-400">E</kbd>`;
      }
    }

    // 4. Update Reference Images & Captions
    if (guide.images) {
      if (this.guideImgStart && guide.images.start) {
        this.guideImgStart.src = guide.images.start.url;
      }
      if (this.guideCaptionStart && guide.images.start) {
        this.guideCaptionStart.textContent = guide.images.start.desc;
      }

      if (this.guideImgKey && guide.images.key) {
        this.guideImgKey.src = guide.images.key.url;
      }
      if (this.guideCaptionKey && guide.images.key) {
        this.guideCaptionKey.textContent = guide.images.key.desc;
      }

      if (this.guideImgEnd && guide.images.end) {
        this.guideImgEnd.src = guide.images.end.url;
      }
      if (this.guideCaptionEnd && guide.images.end) {
        this.guideCaptionEnd.textContent = guide.images.end.desc;
      }
    }

    if (this.guideToolName) this.guideToolName.textContent = guide.tool_name || "";
    if (this.guideToolDetail) this.guideToolDetail.textContent = guide.tool_detail || "";
    if (this.guideCriteria) this.guideCriteria.textContent = guide.criteria || "";
    if (this.guideWarning) this.guideWarning.textContent = guide.warning || "";
  }

  /**
   * Save Annotation via POST /api/annotation
   */
  async saveAnnotation() {
    if (!this.currentVideo) {
      this.showToast("Chưa chọn video để lưu!", "⚠️");
      return;
    }

    // Collect events
    const eventsList = [];
    const validationErrors = [];

    for (const [step, data] of Object.entries(this.eventsByStep)) {
      if (!data) continue;

      const rawS = data.start_sec;
      const rawK = data.key_sec;
      const rawE = data.end_sec;

      const hasS = rawS !== null && rawS !== undefined && rawS !== "" && !isNaN(Number(rawS));
      const hasK = rawK !== null && rawK !== undefined && rawK !== "" && !isNaN(Number(rawK));
      const hasE = rawE !== null && rawE !== undefined && rawE !== "" && !isNaN(Number(rawE));

      const s = hasS ? Number(rawS) : null;
      const k = hasK ? Number(rawK) : null;
      const e = hasE ? Number(rawE) : null;

      // Skip empty steps
      if (s === null && k === null && e === null) continue;

      let label = step;
      if (label === "B6a") label = "B6_clean";
      if (label === "B6b") label = "B6_cut";

      // Validate completeness
      if (s === null || e === null) {
        validationErrors.push(`Bước ${step}: Thiếu mốc START hoặc END`);
        continue;
      }
      if (k === null) {
        validationErrors.push(`Bước ${step}: Thiếu mốc then chốt KEY_TIME`);
        continue;
      }
      if (s >= e) {
        validationErrors.push(`Bước ${step}: START (${s}s) >= END (${e}s)`);
        continue;
      }
      if (k <= s || k >= e) {
        validationErrors.push(`Bước ${step}: KEY_TIME (${k}s) phải nằm giữa START (${s}s) và END (${e}s)`);
        continue;
      }

      eventsList.push({
        label: label,
        start_sec: s,
        key_sec: k,
        end_sec: e
      });
    }

    if (validationErrors.length > 0) {
      this.showToast(`Lỗi: ${validationErrors[0]}`, "❌");
      return;
    }

    const payload = {
      video_path: this.currentVideo.rel_path,
      fps: this.videoInfo.fps || 30.0,
      duration_sec: this.videoInfo.duration_sec || this.videoPlayer?.duration || 0,
      events: eventsList
    };

    try {
      const res = await fetch("/api/annotation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || data.status === "error") {
        const errText = data.errors ? data.errors.join(", ") : "Lỗi lưu nhãn";
        throw new Error(errText);
      }

      // Success
      this.isDirty = false;
      localStorage.removeItem(`kttc_draft_${this.currentVideo.rel_path}`);

      const timeStr = new Date().toLocaleTimeString();
      this.updateSaveStatus(`Đã lưu (${timeStr})`);
      this.showToast("💾 Đã lưu nhãn JSON thành công!", "✅");

      // Update video status badge in playlist
      const activeCount = eventsList.length;
      let newStatus = "not_annotated";
      if (activeCount >= 8) {
        newStatus = "annotated";
      } else if (activeCount > 0) {
        newStatus = "in_progress";
      }

      this.currentVideo.status = newStatus;
      this.updateVideoStatusBadge(newStatus);
      this.updateProgressStats();
      this.renderPlaylist();
    } catch (err) {
      this.showToast(`Lỗi lưu nhãn: ${err.message}`, "❌");
    }
  }

  /**
   * Save LocalStorage draft
   */
  saveLocalDraft() {
    if (!this.currentVideo) return;
    const draftKey = `kttc_draft_${this.currentVideo.rel_path}`;
    localStorage.setItem(
      draftKey,
      JSON.stringify({
        events: this.eventsByStep,
        timestamp: Date.now()
      })
    );
    this.updateSaveStatus("Đã lưu nháp");
  }

  /**
   * Setup 15-second auto-save interval
   */
  initAutoSave() {
    this.autoSaveTimer = setInterval(() => {
      if (this.isDirty && this.currentVideo) {
        this.saveLocalDraft();
      }
    }, 15000);
  }

  /**
   * Update Top Header Save Status
   */
  updateSaveStatus(status) {
    if (!this.saveStatusIndicator) return;
    let dotColor = "bg-slate-500";
    if (status.includes("Đã lưu") || status.includes("Đã đồng bộ")) {
      dotColor = "bg-emerald-400";
    } else if (status.includes("nháp")) {
      dotColor = "bg-amber-400";
    } else if (status.includes("Chưa lưu")) {
      dotColor = "bg-rose-400";
    }

    this.saveStatusIndicator.innerHTML = `<span class="w-2 h-2 rounded-full ${dotColor}"></span> ${status}`;
  }

  /**
   * Update video status badge in center panel
   */
  updateVideoStatusBadge(status) {
    if (!this.videoStatusBadge) return;
    this.videoStatusBadge.className = "px-2 py-0.5 text-[10px] font-bold rounded-full uppercase tracking-wider shrink-0";

    if (status === "annotated") {
      this.videoStatusBadge.classList.add("badge-status-annotated");
      this.videoStatusBadge.textContent = "Đã xong";
    } else if (status === "in_progress") {
      this.videoStatusBadge.classList.add("badge-status-in_progress");
      this.videoStatusBadge.textContent = "Đang gán";
    } else {
      this.videoStatusBadge.classList.add("badge-status-not_annotated");
      this.videoStatusBadge.textContent = "Chưa gán";
    }
  }

  /**
   * Switch Video Relatively (Previous / Next)
   */
  switchVideoRelative(direction = 1) {
    if (this.videos.length === 0) return;
    const nextIdx = this.currentVideoIndex + direction;
    if (nextIdx >= 0 && nextIdx < this.videos.length) {
      this.selectVideo(this.videos[nextIdx]);
    } else {
      this.showToast(direction > 0 ? "Đã ở video cuối cùng!" : "Đã ở video đầu tiên!", "ℹ️");
    }
  }

  /**
   * Slicing Modal Dialog
   */
  openSliceModal() {
    if (!this.currentVideo) {
      this.showToast("Vui lòng chọn video trước khi cắt clip!", "⚠️");
      return;
    }
    if (this.sliceModal) {
      this.sliceModal.classList.remove("hidden");
      this.sliceProgressContainer?.classList.add("hidden");
      if (this.sliceClipsList) this.sliceClipsList.innerHTML = "";
    }
  }

  closeSliceModal() {
    if (this.sliceModal) {
      this.sliceModal.classList.add("hidden");
    }
    if (this.slicePollInterval) {
      clearInterval(this.slicePollInterval);
      this.slicePollInterval = null;
    }
  }

  /**
   * Trigger Slicing Job and poll progress
   */
  async startSlicing() {
    if (!this.currentVideo) return;

    // Collect valid events
    const eventsList = [];
    for (const [step, data] of Object.entries(this.eventsByStep)) {
      if (!data) continue;
      const s = Number(data.start_sec);
      const e = Number(data.end_sec);

      if (s !== null && e !== null && !isNaN(s) && !isNaN(e) && e > s) {
        let label = step;
        if (label === "B6a") label = "B6_clean";
        if (label === "B6b") label = "B6_cut";

        const rawKey = data.key_sec;
        const hasValidKey = rawKey !== null && rawKey !== undefined && rawKey !== "" && !isNaN(Number(rawKey));
        const numKey = hasValidKey ? Number(rawKey) : null;
        const finalKey = (numKey !== null && numKey > s && numKey < e) ? numKey : Number(((s + e) / 2).toFixed(3));

        eventsList.push({
          label: label,
          start_sec: s,
          end_sec: e,
          key_sec: finalKey
        });
      }
    }

    if (eventsList.length === 0) {
      this.showToast("Chưa có bước nào được gán hợp lệ để cắt!", "⚠️");
      return;
    }

    const payload = {
      video_path: this.currentVideo.rel_path,
      events: eventsList,
      slice_b0: this.chkSliceB0 ? this.chkSliceB0.checked : false,
      fast_copy: this.chkFastCopy ? this.chkFastCopy.checked : false
    };

    if (this.sliceProgressContainer) this.sliceProgressContainer.classList.remove("hidden");
    if (this.btnConfirmSlice) this.btnConfirmSlice.disabled = true;
    if (this.sliceProgressBar) this.sliceProgressBar.style.width = "0%";
    if (this.sliceProgressPct) this.sliceProgressPct.textContent = "0%";
    if (this.sliceStatusMsg) this.sliceStatusMsg.textContent = "Đang gửi yêu cầu cắt...";

    try {
      const res = await fetch("/api/slice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || data.status !== "started") {
        throw new Error(data.error || "Không thể khởi động tiến trình cắt");
      }

      this.sliceJobId = data.job_id;
      this.pollSliceProgress(this.sliceJobId);
    } catch (err) {
      if (this.sliceStatusMsg) this.sliceStatusMsg.textContent = `Lỗi: ${err.message}`;
      if (this.btnConfirmSlice) this.btnConfirmSlice.disabled = false;
      this.showToast(`Lỗi cắt video: ${err.message}`, "❌");
    }
  }

  /**
   * Poll Slicing Progress every 500ms
   */
  pollSliceProgress(jobId) {
    if (this.slicePollInterval) clearInterval(this.slicePollInterval);

    this.slicePollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/slice_progress?job_id=${encodeURIComponent(jobId)}`);
        if (!res.ok) {
          clearInterval(this.slicePollInterval);
          return;
        }

        const data = await res.json();
        const pct = data.progress || 0;

        if (this.sliceProgressBar) this.sliceProgressBar.style.width = `${pct}%`;
        if (this.sliceProgressPct) this.sliceProgressPct.textContent = `${pct}%`;
        if (this.sliceStatusMsg) this.sliceStatusMsg.textContent = data.message || "Đang xử lý...";

        if (data.status === "finished") {
          clearInterval(this.slicePollInterval);
          this.slicePollInterval = null;
          if (this.btnConfirmSlice) this.btnConfirmSlice.disabled = false;

          // Render clips list
          if (this.sliceClipsList && Array.isArray(data.clips)) {
            this.sliceClipsList.innerHTML = data.clips
              .map((c) => `<div class="text-emerald-400">✅ ${c}</div>`)
              .join("");
          }
          this.showToast("✂️ Cắt video hoàn tất thành công!", "✅");
        } else if (data.status === "failed") {
          clearInterval(this.slicePollInterval);
          this.slicePollInterval = null;
          if (this.btnConfirmSlice) this.btnConfirmSlice.disabled = false;
          this.showToast(`Lỗi cắt clip: ${data.message}`, "❌");
        }
      } catch (err) {
        console.error("Slice poll error:", err);
      }
    }, 500);
  }

  /**
   * Help Modal Controls
   */
  openHelpModal() {
    this.helpModal?.classList.remove("hidden");
  }

  closeHelpModal() {
    this.helpModal?.classList.add("hidden");
  }

  /**
   * Global Keyboard Shortcuts Handler
   */
  handleGlobalKeyDown(e) {
    // Ignore keystrokes when typing inside inputs / textareas
    if (["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName)) {
      return;
    }

    // Ctrl + S (or Cmd + S) -> Save Annotation
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      this.saveAnnotation();
      return;
    }

    // Alt + N -> Next Video
    if (e.altKey && e.key.toLowerCase() === "n") {
      e.preventDefault();
      this.switchVideoRelative(1);
      return;
    }

    // Alt + P -> Previous Video
    if (e.altKey && e.key.toLowerCase() === "p") {
      e.preventDefault();
      this.switchVideoRelative(-1);
      return;
    }

    // Toggle Left Panel: [ or Alt+1
    if (e.key === "[" || (e.altKey && e.key === "1")) {
      e.preventDefault();
      this.toggleLeftPanel();
      return;
    }

    // Toggle Right Panel: ] or Alt+2
    if (e.key === "]" || (e.altKey && e.key === "2")) {
      e.preventDefault();
      this.toggleRightPanel();
      return;
    }

    // Space -> Play / Pause
    if (e.code === "Space") {
      e.preventDefault();
      this.togglePlayPause();
      return;
    }

    // Frame-accurate navigation
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      if (e.shiftKey) {
        this.stepSeconds(-1.0);
      } else {
        this.stepFrame(-1);
      }
      return;
    }

    if (e.key === "ArrowRight") {
      e.preventDefault();
      if (e.shiftKey) {
        this.stepSeconds(1.0);
      } else {
        this.stepFrame(1);
      }
      return;
    }

    // 3-Point Marking Hotkeys: S, K, E
    if (e.key.toLowerCase() === "s" && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      this.setMark("start");
      return;
    }

    if (e.key.toLowerCase() === "k" && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      this.setMark("key");
      return;
    }

    if (e.key.toLowerCase() === "e" && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      this.setMark("end");
      return;
    }

    // Delete or Backspace -> Clear Active Step
    if (e.key === "Delete" || e.key === "Backspace") {
      e.preventDefault();
      this.clearActiveStep();
      return;
    }

    // Step Quick Switching: 1..9, 0 (avoid collision with Ctrl+1..Ctrl+9 browser tabs)
    if (!e.ctrlKey && !e.altKey && !e.metaKey) {
      if (e.key === "1") { this.setActiveStep("B1"); return; }
      if (e.key === "2") { this.setActiveStep("B2"); return; }
      if (e.key === "3") { this.setActiveStep("B3"); return; }
      if (e.key === "4") { this.setActiveStep("B4"); return; }
      if (e.key === "5") { this.setActiveStep("B5"); return; }
      if (e.key === "6") {
        // Toggle between B6a and B6b
        this.setActiveStep(this.activeStep === "B6a" ? "B6b" : "B6a");
        return;
      }
      if (e.key === "7") { this.setActiveStep("B6b"); return; }
      if (e.key === "8") { this.setActiveStep("B7"); return; }
      if (e.key === "9") { this.setActiveStep("B8"); return; }
      if (e.key === "0") { this.setActiveStep("B9"); return; }
    }

    // Help modal toggle (?)
    if (e.key === "?" || (e.shiftKey && e.key === "/")) {
      e.preventDefault();
      if (this.helpModal?.classList.contains("hidden")) {
        this.openHelpModal();
      } else {
        this.closeHelpModal();
      }
      return;
    }

    // Escape -> Close Modals
    if (e.key === "Escape") {
      this.closeHelpModal();
      this.closeSliceModal();
      return;
    }
  }

  /**
   * Floating Toast Notification
   */
  showToast(message, icon = "ℹ️", duration = 3000) {
    if (!this.toastNotification || !this.toastMessage) return;

    if (this.toastIcon) this.toastIcon.textContent = icon;
    this.toastMessage.textContent = message;

    this.toastNotification.classList.remove("hidden");
    this.toastNotification.classList.add("toast-animate");

    if (this.toastTimeout) clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => {
      this.toastNotification.classList.add("hidden");
      this.toastNotification.classList.remove("toast-animate");
    }, duration);
  }

  /**
   * Utilities
   */
  formatTime(seconds) {
    const totalSec = Math.max(0, Number(seconds) || 0);
    const m = Math.floor(totalSec / 60);
    const s = Math.floor(totalSec % 60);
    const ms = Math.floor((totalSec % 1) * 1000);

    const mm = m.toString().padStart(2, "0");
    const ss = s.toString().padStart(2, "0");
    const mmm = ms.toString().padStart(3, "0");
    return `${mm}:${ss}.${mmm}`;
  }

  /**
   * Safely package and resolve key_sec timestamp within (start_sec, end_sec).
   * Falls back to midpoint if key_sec is missing, null, NaN, or out of bounds.
   */
  static resolveKeySec(rawKey, s, e) {
    const hasValidKey = rawKey !== null && rawKey !== undefined && rawKey !== "" && !isNaN(Number(rawKey));
    const numKey = hasValidKey ? Number(rawKey) : null;
    return (numKey !== null && numKey > s && numKey < e) ? numKey : Number(((s + e) / 2).toFixed(3));
  }

  resolveKeySec(rawKey, s, e) {
    return AppController.resolveKeySec(rawKey, s, e);
  }
}

// Auto-initialize when DOM is ready
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    window.app = new AppController();
  });
}

// Support Node.js / CommonJS
if (typeof module !== "undefined" && module.exports) {
  module.exports = { AppController };
}
