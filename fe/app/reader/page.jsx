'use client';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useApp } from '../../context/AppContext';
import { sendChatMessage } from '../../utils/api';
import FormattedChatMessage from '../../components/FormattedChatMessage';

const COURSE_DOCUMENTS = [
  {
    dayId: '01',
    dayTitle: 'Day 01',
    publishedCount: '1 TÀI LIỆU · PUBLISHED',
    files: [
      {
        id: 'd1_slide',
        name: 'd1-slide-hackathon.pdf',
        pages: 29,
        pdfUrl: '/slides/d1-slide-hackathon.pdf',
        title: 'AI & LLM Foundation',
        subtitle: 'Slide bài giảng Day 1: Tổng quan LLM & Kiến trúc Transformer'
      }
    ]
  },
  {
    dayId: '02',
    dayTitle: 'Day 02',
    publishedCount: '1 TÀI LIỆU · PUBLISHED',
    files: [
      {
        id: 'd2_slide',
        name: 'd2-slide-hackathon.pdf',
        pages: 29,
        pdfUrl: '/slides/d2-slide-hackathon.pdf',
        title: 'Xác định bài toán cho AI',
        subtitle: 'Slide bài giảng Day 2: Problem Statement & Customer Evidence'
      }
    ]
  }
];

function PdfSlideViewer({ pdfUrl, currentPage, zoomLevel = 100, userEmail }) {
  const canvasRef = useRef(null);
  const [pdfDoc, setPdfDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [renderError, setRenderError] = useState(false);

  useEffect(() => {
    if (!pdfUrl) return;
    setLoading(true);
    setRenderError(false);

    const initPdfJs = () => {
      if (!window.pdfjsLib) {
        setRenderError(true);
        setLoading(false);
        return;
      }
      window.pdfjsLib.GlobalWorkerOptions.workerSrc =
        'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

      window.pdfjsLib
        .getDocument(pdfUrl)
        .promise.then(doc => {
          setPdfDoc(doc);
          setLoading(false);
        })
        .catch(() => {
          setRenderError(true);
          setLoading(false);
        });
    };

    if (!window.pdfjsLib) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
      script.onload = initPdfJs;
      script.onerror = () => {
        setRenderError(true);
        setLoading(false);
      };
      document.head.appendChild(script);
    } else {
      initPdfJs();
    }
  }, [pdfUrl]);

  useEffect(() => {
    if (!pdfDoc || !canvasRef.current) return;
    const pageNum = Math.min(Math.max(1, currentPage), pdfDoc.numPages);

    pdfDoc.getPage(pageNum).then(page => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      const targetWidth = Math.min(typeof window !== 'undefined' ? window.innerWidth - 360 : 800, 820) * (zoomLevel / 100);
      const baseViewport = page.getViewport({ scale: 1.0 });
      const scale = targetWidth / baseViewport.width;
      const viewport = page.getViewport({ scale: Math.max(0.5, scale) });

      canvas.width = viewport.width;
      canvas.height = viewport.height;

      page.render({
        canvasContext: ctx,
        viewport: viewport
      });
    });
  }, [pdfDoc, currentPage, zoomLevel]);

  if (renderError) {
    return (
      <div className="w-full h-full min-h-[500px] bg-white rounded-2xl overflow-hidden relative border-0 flex items-center justify-center">
        <iframe
          key={`${pdfUrl}-p${currentPage}`}
          src={`${pdfUrl}#page=${currentPage}&toolbar=0&navpanes=0&scrollbar=0&view=Fit`}
          className="w-full h-full min-h-[500px] border-0 bg-white rounded-2xl"
          style={{ overflow: 'hidden' }}
          scrolling="no"
          title="PDF Slide Page"
        />
      </div>
    );
  }

  return (
    <div className="w-full h-full flex items-center justify-center relative overflow-hidden bg-slate-900 rounded-2xl min-h-[500px] select-none">
      {loading && (
        <div className="text-slate-300 text-xs font-semibold animate-pulse">
          Đang tải slide trang {currentPage}...
        </div>
      )}
      <div className="relative shadow-2xl rounded-xl overflow-hidden bg-white max-w-full my-auto border border-slate-200 dark:border-slate-800">
        <canvas ref={canvasRef} className="block max-w-full h-auto rounded-xl" />
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-10 transform -rotate-12 select-none font-black text-sm md:text-base tracking-widest text-slate-900 whitespace-nowrap">
          {userEmail || '26AI.TRUONGVH@VINUNI.EDU.VN'}
        </div>
      </div>
    </div>
  );
}

export default function SlideReaderPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { lang, toggleLang, dark, toggleDark, user } = useApp();
  const isVi = lang === 'VI';

  // Language Dictionary
  const t = {
    backToCourses: isVi ? 'Quay lại danh sách khóa học' : 'Back to Courses',
    courseMaterials: isVi ? 'Học liệu môn học' : 'Course Materials',
    subtitleMaterials: isVi ? 'Slide bài giảng chính thức' : 'Official Lecture Slides',
    pages: isVi ? 'trang' : 'pages',
    read: isVi ? 'Đọc' : 'Read',
    pen: isVi ? 'Bút' : 'Pen',
    highlight: isVi ? 'Highlight' : 'Highlight',
    page: isVi ? 'Trang' : 'Page',
    note: isVi ? 'ghi chú' : 'notes',
    addNote: isVi ? 'Thêm ghi chú' : 'Add Note',
    downloadDoc: isVi ? 'Tải xuống tài liệu' : 'Download Document',
    undoDraw: isVi ? 'Hoàn tác nét vẽ' : 'Undo Line',
    clearAll: isVi ? 'Xóa tất cả chú thích' : 'Clear All Annotations',
    prevPage: isVi ? 'Trang trước' : 'Previous Page',
    nextPage: isVi ? 'Trang tiếp theo' : 'Next Page',
    studyingBadge: isVi ? 'ĐANG HỌC' : 'STUDYING',
    aiTutor: isVi ? 'VLearn AI Tutor' : 'VLearn AI Tutor',
    aiPlaceholder: isVi ? 'Hỏi AI Tutor về slide này...' : 'Ask AI Tutor about this slide...',
    send: isVi ? 'Gửi' : 'Send',
    thinking: isVi ? 'AI Tutor đang suy nghĩ...' : 'AI Tutor is thinking...',
    welcomeChat: isVi
      ? 'Xin chào! Tôi là VLearn AI Tutor. Tôi đang cùng bạn học slide bài giảng này. Bạn cần trợ giúp giải thích khái niệm nào không?'
      : 'Hello! I am VLearn AI Tutor. I am studying this slide with you. How can I assist you?'
  };

  // Selected file & studying day state
  const initialFileName = searchParams.get('file') || 'd1-slide-hackathon.pdf';
  const initialDayId = searchParams.get('day') || '01';

  const [studyingDayId, setStudyingDayId] = useState(initialDayId);
  const [activeDayId, setActiveDayId] = useState(initialDayId);
  const [activeFile, setActiveFile] = useState(() => {
    for (const group of COURSE_DOCUMENTS) {
      const match = group.files.find(f => f.name.toLowerCase() === initialFileName.toLowerCase() || f.id === initialFileName);
      if (match) return match;
    }
    return COURSE_DOCUMENTS[0].files[0];
  });

  // Sidebar collapse state
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [expandedDays, setExpandedDays] = useState({ '01': true, '02': true });

  // Reading tools state
  const [activeTool, setActiveTool] = useState('read');
  const [currentPage, setCurrentPage] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [notes, setNotes] = useState([{ id: 1, page: 1, text: isVi ? 'Ghi chú học tập' : 'Study note' }]);

  // Canvas drawing state
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawings, setDrawings] = useState([]);

  // AI Tutor drawer state
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: t.welcomeChat,
      time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const maxPages = activeFile.pages || 29;

  // Smooth Page Change Function
  function changePage(newPage) {
    if (newPage < 1 || newPage > maxPages || isTransitioning) return;
    setIsTransitioning(true);
    setCurrentPage(newPage);
    setTimeout(() => {
      setIsTransitioning(false);
    }, 150);
  }

  // Handle Download File
  function handleDownloadFile(fileToDownload) {
    const targetFile = fileToDownload || activeFile;
    if (!targetFile || !targetFile.pdfUrl) return;

    const link = document.createElement('a');
    link.href = targetFile.pdfUrl;
    link.download = targetFile.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Handle Canvas Drawings Redraw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawings.filter(d => d.page === currentPage && d.fileId === activeFile.id).forEach(stroke => {
      ctx.beginPath();
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.width;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      stroke.points.forEach((pt, idx) => {
        if (idx === 0) ctx.moveTo(pt.x, pt.y);
        else ctx.lineTo(pt.x, pt.y);
      });
      ctx.stroke();
    });
  }, [currentPage, drawings, zoomLevel, activeFile]);

  function handleMouseDown(e) {
    if (activeTool === 'read') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setIsDrawing(true);

    const newStroke = {
      fileId: activeFile.id,
      page: currentPage,
      tool: activeTool,
      color: activeTool === 'highlight' ? 'rgba(253, 224, 71, 0.45)' : '#E11D48',
      width: activeTool === 'highlight' ? 18 : 3,
      points: [{ x, y }]
    };
    setDrawings(prev => [...prev, newStroke]);
  }

  function handleMouseMove(e) {
    if (!isDrawing || activeTool === 'read') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setDrawings(prev => {
      if (prev.length === 0) return prev;
      const last = { ...prev[prev.length - 1] };
      last.points = [...last.points, { x, y }];
      return [...prev.slice(0, -1), last];
    });
  }

  function handleMouseUp() {
    setIsDrawing(false);
  }

  function toggleDayAccordion(dayId) {
    setExpandedDays(prev => ({ ...prev, [dayId]: !prev[dayId] }));
  }

  function selectFile(group, file) {
    if (activeFile.id === file.id) return;
    setIsTransitioning(true);
    setStudyingDayId(group.dayId);
    setActiveDayId(group.dayId);
    setActiveFile(file);
    setCurrentPage(1);

    setTimeout(() => {
      setIsTransitioning(false);
    }, 180);
  }

  async function handleSendAiChat(e) {
    e.preventDefault();
    if (!inputMsg.trim() || isLoading) return;

    const userText = inputMsg.trim();
    const userMsgObj = {
      id: Date.now(),
      sender: 'user',
      text: userText,
      time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsgObj]);
    setInputMsg('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: userText,
        context: {
          course_id: 'comp2010-phase-1',
          current_lecture_id: activeFile.name.includes('d1') ? 'day-01' : 'day-02',
          current_page: currentPage
        }
      });

      const aiMsgObj = {
        id: Date.now() + 1,
        sender: 'ai',
        text: response.answer,
        citations: response.citations || [],
        time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsgObj]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'ai',
          text: isVi ? 'Không thể kết nối máy chủ AI Tutor. Vui lòng kiểm tra backend.' : 'Could not connect to AI Tutor backend server.',
          time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="h-screen flex flex-col bg-[#F1F5F9] dark:bg-[#0F172A] overflow-hidden transition-colors duration-200">
      {/* Top Header Bar with Language & Dark Mode Controls */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-800 px-4 py-2.5 flex items-center justify-between z-30 transition-colors">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-1.5 text-xs font-bold text-[#0B3B60] dark:text-[#38BDF8] hover:underline"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            <span>{t.backToCourses}</span>
          </button>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <h1 className="text-xs font-extrabold text-slate-800 dark:text-slate-100">{activeFile.title || activeFile.name}</h1>
          </div>
        </div>

        {/* Right Header Action Icons: Language Toggle (VI/EN) & Dark Mode Toggle (☀️/🌙) */}
        <div className="flex items-center gap-2.5">
          {/* Language Toggle Button */}
          <button
            onClick={toggleLang}
            className="px-2.5 py-1 rounded-lg text-xs font-extrabold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700 flex items-center gap-1 cursor-pointer"
            title={isVi ? 'Đổi sang Tiếng Anh (English)' : 'Đổi sang Tiếng Việt (Vietnamese)'}
          >
            <span>🌐</span>
            <span>{lang === 'VI' ? 'VI' : 'EN'}</span>
          </button>

          {/* Dark Mode Toggle Button */}
          <button
            onClick={toggleDark}
            className="p-1.5 rounded-lg text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700 flex items-center justify-center w-8 h-8 cursor-pointer"
            title={dark ? 'Chuyển sang Chế độ Sáng (Light Mode)' : 'Chuyển sang Chế độ Tối (Dark Mode)'}
          >
            <span>{dark ? '☀️' : '🌙'}</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="flex-1 flex relative overflow-hidden">
        {/* Sidebar Left Navigation Accordion Panel */}
        <aside
          className={`bg-[#F8FAFC] dark:bg-[#0F172A] border-r border-slate-200 dark:border-slate-800 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] z-20 flex flex-col shadow-lg overflow-hidden ${
            sidebarOpen ? 'w-72 opacity-100' : 'w-0 opacity-0 pointer-events-none'
          }`}
        >
          {/* Sidebar Top Title Header */}
          <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1E293B] transition-colors">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#0B3B60] text-white flex items-center justify-center font-bold text-xs">
                📚
              </div>
              <div>
                <h2 className="text-xs font-extrabold text-slate-900 dark:text-white uppercase tracking-wider">{t.courseMaterials}</h2>
                <p className="text-[10px] text-slate-500 dark:text-slate-400">{t.subtitleMaterials}</p>
              </div>
            </div>
          </div>

          {/* Sidebar Course Documents Accordion List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {COURSE_DOCUMENTS.map(group => {
              const isOpen = expandedDays[group.dayId] ?? true;
              const isStudying = studyingDayId === group.dayId;

              return (
                <div
                  key={group.dayId}
                  className="rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-[#1E293B] overflow-hidden shadow-xs"
                >
                  {/* Group Header Button */}
                  <button
                    onClick={() => toggleDayAccordion(group.dayId)}
                    className="w-full p-3.5 flex items-center justify-between bg-slate-50/80 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 flex items-center justify-center font-black text-xs">
                        {group.dayId}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">{group.dayTitle}</span>
                          {isStudying && (
                            <span className="text-[9px] font-extrabold px-2 py-0.5 rounded-full bg-blue-100 text-[#0B3B60] dark:bg-blue-900/80 dark:text-[#38BDF8] border border-blue-200 dark:border-blue-700 animate-pulse">
                              {t.studyingBadge}
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 dark:text-slate-500">{group.publishedCount}</div>
                      </div>
                    </div>
                    <svg
                      width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                      className={`transition-transform duration-300 text-slate-400 ${isOpen ? 'rotate-180' : ''}`}
                    >
                      <path d="M6 9l6 6 6-6" />
                    </svg>
                  </button>

                  {/* Accordion Files List */}
                  <div className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'max-h-96 opacity-100 p-2 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-[#1E293B]' : 'max-h-0 opacity-0 p-0 border-t-0'}`}>
                    <div className="space-y-1.5">
                      {group.files.map(file => {
                        const isActive = activeFile.name === file.name;
                        return (
                          <div
                            key={file.id}
                            onClick={() => selectFile(group, file)}
                            className={`p-2.5 rounded-xl border transition-all duration-200 cursor-pointer flex items-center justify-between group/item ${
                              isActive
                                ? 'border-[#0B3B60] dark:border-[#38BDF8] bg-blue-50/70 dark:bg-blue-950/50 shadow-xs'
                                : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                            }`}
                          >
                            <div className="flex items-center gap-2 min-w-0 pr-2">
                              <span className="text-xs">📄</span>
                              <div className="truncate">
                                <div className={`text-xs font-semibold truncate ${isActive ? 'text-[#0B3B60] dark:text-[#38BDF8]' : 'text-slate-800 dark:text-slate-200'}`}>
                                  {file.name}
                                </div>
                                <div className="text-[10px] text-slate-400 dark:text-slate-500">{file.pages} {t.pages}</div>
                              </div>
                            </div>
                            <div className="flex items-center gap-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDownloadFile(file);
                                }}
                                className="p-1 rounded-md text-slate-400 hover:text-[#0B3B60] dark:hover:text-[#38BDF8] hover:bg-slate-200 dark:hover:bg-slate-700 transition-all opacity-0 group-hover/item:opacity-100"
                                title={`Tải ${file.name}`}
                              >
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                  <polyline points="7 10 12 15 17 10" />
                                  <line x1="12" y1="15" x2="12" y2="3" />
                                </svg>
                              </button>
                              {isActive && (
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-[#0B3B60] dark:text-[#38BDF8]">
                                  <polyline points="20 6 9 17 4 12" />
                                </svg>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Sidebar Toggle Edge Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-1/2 -translate-y-1/2 z-30 w-7 h-12 bg-white dark:bg-[#1E293B] border border-slate-200 dark:border-slate-700 rounded-r-xl shadow-xl flex items-center justify-center text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] cursor-pointer hover:w-9 hover:bg-slate-50 dark:hover:bg-slate-800"
          style={{ left: sidebarOpen ? '288px' : '0px' }}
          title={sidebarOpen ? 'Thu gọn học liệu' : 'Mở học liệu môn học'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className={`transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${sidebarOpen ? '' : 'rotate-180'}`}>
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>

        {/* Center Main Workspace Canvas Area */}
        <div className="flex-1 flex flex-col bg-[#F1F5F9] dark:bg-[#0B132B] relative overflow-hidden transition-colors duration-300">
          {/* Top Control Floating Toolbar */}
          <div className="p-3 flex justify-center z-10">
            <div className="bg-white/90 dark:bg-[#1E293B]/90 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-md rounded-full px-4 py-1.5 flex items-center gap-3 text-xs font-semibold transition-colors duration-300">
              {/* Reading Tool Selection */}
              <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-full border border-slate-200/60 dark:border-slate-700/60">
                <button
                  onClick={() => setActiveTool('read')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full transition-all ${
                    activeTool === 'read'
                      ? 'bg-white dark:bg-slate-700 text-[#0B3B60] dark:text-[#38BDF8] shadow-xs font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <span>{t.read}</span>
                </button>

                <button
                  onClick={() => setActiveTool('pen')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full transition-all ${
                    activeTool === 'pen'
                      ? 'bg-white dark:bg-slate-700 text-[#0B3B60] dark:text-[#38BDF8] shadow-xs font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                  <span>{t.pen}</span>
                </button>

                <button
                  onClick={() => setActiveTool('highlight')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full transition-all ${
                    activeTool === 'highlight'
                      ? 'bg-white dark:bg-slate-700 text-[#0B3B60] dark:text-[#38BDF8] shadow-xs font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                  <span>{t.highlight}</span>
                </button>
              </div>

              <div className="h-4 w-px bg-slate-200 dark:bg-slate-700"></div>

              {/* Status Badge */}
              <span className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-[11px] font-bold text-slate-700 dark:text-slate-300">
                {t.page} {currentPage} / {maxPages} · {notes.length} {t.note}
              </span>

              <div className="h-4 w-px bg-slate-200 dark:bg-slate-700"></div>

              {/* Zoom Controls */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setZoomLevel(prev => Math.max(50, prev - 15))}
                  className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold cursor-pointer"
                >
                  -
                </button>
                <span className="text-xs font-bold w-10 text-center">{zoomLevel}%</span>
                <button
                  onClick={() => setZoomLevel(prev => Math.min(200, prev + 15))}
                  className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold cursor-pointer"
                >
                  +
                </button>
              </div>

              <div className="h-4 w-px bg-slate-200 dark:bg-slate-700"></div>

              {/* Page Action Tools */}
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <button
                  onClick={() => setNotes(prev => [...prev, { id: Date.now(), page: currentPage, text: isVi ? 'Ghi chú mới' : 'New note' }])}
                  className="hover:text-slate-900 dark:hover:text-white p-1 text-base font-bold cursor-pointer"
                  title={t.addNote}
                >
                  +
                </button>
                <button
                  onClick={() => handleDownloadFile(activeFile)}
                  className="hover:text-slate-900 dark:hover:text-white p-1 cursor-pointer"
                  title={t.downloadDoc}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                </button>
                <button
                  onClick={() => setDrawings(prev => prev.slice(0, -1))}
                  className="hover:text-slate-900 dark:hover:text-white p-1 cursor-pointer"
                  title={t.undoDraw}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="1 4 1 10 7 10" />
                    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                  </svg>
                </button>
                <button
                  onClick={() => setDrawings([])}
                  className="hover:text-red-500 p-1 cursor-pointer"
                  title={t.clearAll}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Main Slide Notebook Viewer Canvas Area */}
          <div className="flex-1 overflow-auto p-6 flex justify-center items-center relative">
            <div className="relative flex items-center justify-center w-full max-w-5xl my-auto">

              {/* LEFT Edge Page Navigation Button (< Previous Page) */}
              <button
                disabled={currentPage <= 1}
                onClick={() => changePage(currentPage - 1)}
                className={`absolute left-2 lg:left-6 z-20 w-11 h-11 rounded-full border border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-[#1E293B]/95 text-slate-700 dark:text-slate-200 flex items-center justify-center transition-all duration-300 ${
                  currentPage <= 1
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:scale-110 hover:bg-[#0B3B60] hover:text-white dark:hover:bg-[#38BDF8] dark:hover:text-slate-900 shadow-md cursor-pointer'
                }`}
                title={t.prevPage}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
              </button>

              {/* Center Real Document Viewer Container (Zero Scrollbars Single Slide Card) */}
              <div
                className={`bg-white dark:bg-[#1E293B] rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-4 relative flex flex-col transition-all duration-300 transform ${
                  isTransitioning ? 'opacity-30 scale-98 translate-y-1' : 'opacity-100 scale-100 translate-y-0'
                } ease-out`}
                style={{
                  width: `${Math.round(850 * (zoomLevel / 100))}px`,
                  minHeight: `${Math.round(540 * (zoomLevel / 100))}px`,
                }}
              >
                {/* Header Meta */}
                <div className="flex items-center justify-between text-xs font-semibold text-slate-400 dark:text-slate-500 mb-3 px-2">
                  <span>{t.page} {currentPage} / {maxPages}</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">{activeFile.name}</span>
                </div>

                {/* Real Native PDF Viewer Container Page-by-Page with ZERO scrollbar */}
                <div className="flex-1 rounded-2xl overflow-hidden bg-[#3A4F41] relative shadow-inner border border-slate-200 dark:border-slate-800 flex flex-col min-h-[500px]">
                  <PdfSlideViewer
                    pdfUrl={activeFile.pdfUrl}
                    currentPage={currentPage}
                    zoomLevel={zoomLevel}
                    userEmail={user?.email}
                  />

                  {/* Canvas Drawing Overlay Layer */}
                  <canvas
                    ref={canvasRef}
                    width={800}
                    height={500}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                    className={`absolute inset-0 w-full h-full z-20 ${
                      activeTool !== 'read' ? 'cursor-crosshair pointer-events-auto' : 'pointer-events-none'
                    }`}
                  />
                </div>

                {/* Display Sticky Notes */}
                {notes.filter(n => n.page === currentPage).map(note => (
                  <div
                    key={note.id}
                    className="absolute bottom-8 right-8 bg-amber-100 dark:bg-amber-900/90 text-amber-900 dark:text-amber-100 p-3 rounded-xl shadow-lg border border-amber-200 text-xs w-52 z-30"
                  >
                    <div className="font-bold border-b border-amber-200 pb-1 mb-1 flex justify-between">
                      <span>Note {t.page} {currentPage}</span>
                      <button onClick={() => setNotes(prev => prev.filter(n => n.id !== note.id))} className="text-amber-700 font-bold">×</button>
                    </div>
                    <p>{note.text}</p>
                  </div>
                ))}
              </div>

              {/* RIGHT Edge Page Navigation Button */}
              <button
                disabled={currentPage >= maxPages}
                onClick={() => changePage(currentPage + 1)}
                className={`absolute right-2 lg:right-6 z-20 w-11 h-11 rounded-full border border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-[#1E293B]/95 text-slate-700 dark:text-slate-200 flex items-center justify-center transition-all duration-300 ${
                  currentPage >= maxPages
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:scale-110 hover:bg-[#0B3B60] hover:text-white dark:hover:bg-[#38BDF8] dark:hover:text-slate-900 shadow-md cursor-pointer'
                }`}
                title={t.nextPage}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </button>
            </div>
          </div>

          {/* Bottom Floating Bar */}
          <div className="p-3 flex justify-center z-10">
            <div className="bg-white/90 dark:bg-[#1E293B]/90 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-md rounded-full px-5 py-1.5 flex items-center gap-4 text-xs font-bold">
              <span className="text-slate-700 dark:text-slate-300 font-extrabold min-w-[100px] text-center">
                {t.page} {currentPage} / {maxPages}
              </span>
            </div>
          </div>

          {/* Floating AI Tutor Drawer Trigger Button */}
          <button
            onClick={() => setAiDrawerOpen(true)}
            className="fixed right-5 bottom-20 z-40 w-12 h-12 bg-gradient-to-r from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6] text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-all border-2 border-white/40 cursor-pointer"
            title="Chat cùng VLearn AI Tutor"
          >
            <span className="text-xl">🤖</span>
          </button>
        </div>

        {/* AI Tutor Slide-Over Drawer */}
        {aiDrawerOpen && (
          <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-[#1E293B] border-l border-slate-200 dark:border-slate-800 shadow-2xl z-50 flex flex-col transition-all duration-300">
            {/* Drawer Header */}
            <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-[#0B3B60] text-white flex items-center justify-center font-bold text-sm">
                  🤖
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t.aiTutor}</h3>
                  <div className="flex items-center gap-1 text-[10px] text-emerald-600 font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Online
                  </div>
                </div>
              </div>
              <button
                onClick={() => setAiDrawerOpen(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/40 dark:bg-slate-900/20">
              {messages.map(msg => (
                <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`max-w-[85%] p-3 rounded-2xl text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-[#0B3B60] text-white rounded-br-none'
                        : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-bl-none shadow-xs'
                    }`}
                  >
                    <FormattedChatMessage content={msg.text} isUser={msg.sender === 'user'} />
                  </div>
                  <span className="text-[9px] text-slate-400 mt-1 px-1">{msg.time}</span>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="animate-spin">⏳</span> {t.thinking}
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSendAiChat} className="p-3 border-t border-slate-100 dark:border-slate-800 flex gap-2">
              <input
                type="text"
                value={inputMsg}
                onChange={e => setInputMsg(e.target.value)}
                placeholder={t.aiPlaceholder}
                className="flex-1 px-3 py-2 rounded-xl text-xs border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:border-[#0B3B60]"
              />
              <button
                type="submit"
                disabled={!inputMsg.trim() || isLoading}
                className="px-4 py-2 bg-[#0B3B60] text-white rounded-xl text-xs font-bold disabled:opacity-50 cursor-pointer"
              >
                {t.send}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
