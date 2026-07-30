'use client';
import Header from '../../components/Header'
import { useEffect, useState, useRef } from 'react'
import { getCourseInfo, getCourseDays, sendChatMessage } from '../../utils/api'
import { useApp } from '../../context/AppContext'

const STORAGE_KEY_CHAT = 'vlearn_notebook_chat'
const STORAGE_KEY_NOTES = 'vlearn_notebook_notes'

export default function NotebookPage() {
  const { lang } = useApp()
  const isVi = lang === 'VI'

  const [info, setInfo] = useState(null)
  const [days, setDays] = useState([])
  const [activeTab, setActiveTab] = useState('progress') // 'progress' | 'chat' | 'notes'
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [notes, setNotes] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [chatError, setChatError] = useState('')
  const chatEndRef = useRef(null)

  // Translations
  const t = {
    notebookTitle: isVi ? 'Sổ tay học tập' : 'Learning Notebook',
    notebookDesc: isVi ? 'Theo dõi tiến trình, lịch sử chat AI và ghi chú cá nhân' : 'Track progress, AI chat history and personal notes',
    tabProgress: isVi ? 'Tiến trình học' : 'Learning Progress',
    tabChat: isVi ? 'Chat với AI Tutor' : 'Chat with AI Tutor',
    tabNotes: isVi ? 'Ghi chú cá nhân' : 'Personal Notes',
    progressOverview: isVi ? 'Tổng quan tiến trình' : 'Progress Overview',
    courseLabel: isVi ? 'Khóa học:' : 'Course:',
    completedLabel: isVi ? 'Đã hoàn thành:' : 'Completed:',
    daysLabel: isVi ? 'ngày' : 'days',
    totalAiQuestions: isVi ? 'Tổng câu hỏi AI:' : 'Total AI questions:',
    dailyDetails: isVi ? 'Chi tiết từng ngày' : 'Daily Details',
    completedStatus: isVi ? 'Hoàn thành' : 'Completed',
    incompletedStatus: isVi ? 'Chưa hoàn thành' : 'Incomplete',
    clearHistory: isVi ? 'Xóa lịch sử' : 'Clear history',
    startAiChat: isVi ? 'Bắt đầu trò chuyện với AI Tutor' : 'Start chatting with AI Tutor',
    aiSubtitle: isVi ? 'Hỏi bất kì điều gì về bài học, khái niệm hoặc bài tập' : 'Ask anything about lessons, concepts or assignments',
    typePlaceholder: isVi ? 'Nhập câu hỏi cho AI Tutor...' : 'Type a question for AI Tutor...',
    autoSaved: isVi ? 'Tự động lưu' : 'Auto-saved',
    notesPlaceholder: isVi
      ? `Viết ghi chú của bạn tại đây... ✍️\n\nVí dụ:\n- Kiến thức cần ôn lại\n- Câu hỏi muốn hỏi giảng viên\n- Ý tưởng cho dự án\n- Ghi nhớ quan trọng từ bài học`
      : `Write your notes here... ✍️\n\nExample:\n- Knowledge to review\n- Questions for instructor\n- Project ideas\n- Key takeaways from lessons`,
    characters: isVi ? 'ký tự' : 'characters',
    clearNotes: isVi ? 'Xóa ghi chú' : 'Clear notes',
  }

  // Load data
  useEffect(() => {
    getCourseInfo().then(setInfo).catch(() => {})
    getCourseDays().then(setDays).catch(() => {})
  }, [])

  // Load persisted data from localStorage
  useEffect(() => {
    try {
      const savedChat = localStorage.getItem(STORAGE_KEY_CHAT)
      if (savedChat) setChatMessages(JSON.parse(savedChat))
      const savedNotes = localStorage.getItem(STORAGE_KEY_NOTES)
      if (savedNotes) setNotes(savedNotes)
    } catch {}
  }, [])

  // Persist chat
  useEffect(() => {
    if (chatMessages.length > 0) {
      localStorage.setItem(STORAGE_KEY_CHAT, JSON.stringify(chatMessages))
    }
  }, [chatMessages])

  // Persist notes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_NOTES, notes)
  }, [notes])

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isTyping])

  async function handleSendMessage(e) {
    e?.preventDefault()
    if (!chatInput.trim()) return

    const message = chatInput.trim()
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: message,
      time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
    }
    setChatMessages(prev => [...prev, userMsg])
    setChatInput('')
    setIsTyping(true)
    setChatError('')

    try {
      const response = await sendChatMessage({
        message,
        context: { course_id: 'comp2010-phase-1' }
      })
      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        content: response.answer,
        status: response.status,
        scope: response.scope,
        citations: response.citations || [],
        suggestedQuestions: response.suggested_questions || [],
        time: new Date().toLocaleTimeString(isVi ? 'vi-VN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
      }
      setChatMessages(prev => [...prev, aiMsg])
    } catch {
      setChatError('Không kết nối được VLearn Tutor. Hãy kiểm tra backend và thử lại.')
    } finally {
      setIsTyping(false)
    }
  }

  function clearChat() {
    setChatMessages([])
    localStorage.removeItem(STORAGE_KEY_CHAT)
  }

  const completedDays = days.filter(d => d.is_completed).length
  const totalDays = days.length || 4
  const progressPercent = Math.round((completedDays / totalDays) * 100)

  const tabs = [
    { key: 'progress', label: t.tabProgress, icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    )},
    { key: 'chat', label: t.tabChat, icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    )},
    { key: 'notes', label: t.tabNotes, icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    )},
  ]

  return (
    <div className="min-h-screen bg-[#F1F5F9] dark:bg-[#0F172A] transition-colors duration-200">
      <Header />

      {/* Page header */}
      <div className="bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="container-centered py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6] flex items-center justify-center shadow-sm">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">{t.notebookTitle}</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t.notebookDesc}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-800 sticky top-0 z-20 transition-colors">
        <div className="container-centered">
          <div className="flex gap-1">
            {tabs.map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all ${
                  activeTab === tab.key
                    ? 'border-[#0B3B60] dark:border-[#38BDF8] text-[#0B3B60] dark:text-[#38BDF8]'
                    : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                {tab.icon}
                {tab.label}
                {tab.key === 'chat' && chatMessages.length > 0 && (
                  <span className="ml-1 bg-[#0B3B60] dark:bg-[#38BDF8] text-white dark:text-slate-900 text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                    {chatMessages.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      <main className="container-centered py-6">
        {/* PROGRESS TAB */}
        {activeTab === 'progress' && (
          <div className="space-y-5">
            {/* Overview card */}
            <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">{t.progressOverview}</h2>
              <div className="flex items-center gap-6">
                {/* Circular progress */}
                <div className="relative w-24 h-24 flex-shrink-0">
                  <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="#f1f5f9" className="dark:stroke-slate-800" strokeWidth="8"/>
                    <circle
                      cx="50" cy="50" r="42" fill="none"
                      stroke="url(#progressGrad)" strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${progressPercent * 2.64} 264`}
                      className="transition-all duration-700"
                    />
                    <defs>
                      <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#0B3B60"/>
                        <stop offset="100%" stopColor="#1565A8"/>
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xl font-extrabold text-slate-900 dark:text-white">{progressPercent}%</span>
                  </div>
                </div>
                <div className="flex-1 space-y-2">
                  <div className="text-sm text-slate-500 dark:text-slate-400">{t.courseLabel} <strong className="text-slate-900 dark:text-white">{info?.title || 'COMP2010'}</strong></div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">{t.completedLabel} <strong className="text-emerald-600 dark:text-emerald-400">{completedDays}/{totalDays} {t.daysLabel}</strong></div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">{t.totalAiQuestions} <strong className="text-slate-900 dark:text-white">{chatMessages.filter(m => m.role === 'user').length}</strong></div>
                </div>
              </div>
            </div>

            {/* Day-by-day progress */}
            <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">{t.dailyDetails}</h2>
              <div className="space-y-3">
                {(days.length > 0 ? days : [
                  {id:1, seq:'01', title:'Day01', slides:2, is_completed:false},
                  {id:2, seq:'02', title:'Day02', slides:1, is_completed:false},
                  {id:3, seq:'03', title:'Day03', slides:2, is_completed:false},
                  {id:4, seq:'04', title:'Day04', slides:3, is_completed:false},
                ]).map(day => (
                  <div key={day.id} className="flex items-center gap-4 p-3 rounded-xl bg-slate-50/60 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      day.is_completed
                        ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                    }`}>
                      {day.is_completed ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="10"/>
                        </svg>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-semibold text-slate-900 dark:text-white">{day.title}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">{day.slides} slide</div>
                    </div>
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                      day.is_completed
                        ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
                        : 'bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800'
                    }`}>
                      {day.is_completed ? t.completedStatus : t.incompletedStatus}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* CHAT TAB */}
        {activeTab === 'chat' && (
          <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 280px)', minHeight: '500px' }}>
            {/* Chat header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6] flex items-center justify-center">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                    <path d="M12 2a5 5 0 0 1 5 5c0 2.76-2.24 5-5 5s-5-2.24-5-5a5 5 0 0 1 5-5z"/>
                    <path d="M20 21v-1a5 5 0 0 0-5-5H9a5 5 0 0 0-5 5v1"/>
                  </svg>
                </div>
                <div>
                  <div className="text-sm font-bold text-slate-900 dark:text-white">VLearn AI Tutor</div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">Online</span>
                  </div>
                </div>
              </div>
              {chatMessages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="text-xs text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 px-3 py-1.5 rounded-lg transition-colors"
                >
                  {t.clearHistory}
                </button>
              )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {chatMessages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-16 h-16 rounded-2xl bg-slate-50 dark:bg-slate-800 flex items-center justify-center mb-4">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">{t.startAiChat}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{t.aiSubtitle}</p>
                </div>
              )}

              {chatMessages.map(msg => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6] text-white'
                      : 'bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/60 text-slate-800 dark:text-slate-100'
                  }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    {msg.role !== 'user' && msg.citations?.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 space-y-1.5">
                        <div className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                          {isVi ? 'Nguồn từ slide' : 'Slide sources'}
                        </div>
                        {msg.citations.map(citation => (
                          <div key={citation.source_id} className="text-xs text-[#1565A8] dark:text-sky-400">
                            {citation.lecture_title} · {isVi ? 'trang' : 'page'} {citation.page ?? '?'}
                            {citation.excerpt && (
                              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                                {citation.excerpt}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    {msg.role !== 'user' && msg.status && (
                      <div className="mt-2 text-[10px] uppercase tracking-wide text-slate-400">
                        {msg.status} · {msg.scope}
                      </div>
                    )}
                    <div className={`text-[10px] mt-1.5 ${msg.role === 'user' ? 'text-blue-200' : 'text-[#94A3B8]'}`}>
                      {msg.time}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/60 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600 animate-bounce" style={{animationDelay:'0ms'}}></span>
                      <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600 animate-bounce" style={{animationDelay:'150ms'}}></span>
                      <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600 animate-bounce" style={{animationDelay:'300ms'}}></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {chatError && (
              <div className="mx-6 mb-2 rounded-lg bg-red-50 dark:bg-red-950/40 px-3 py-2 text-xs text-red-600 dark:text-red-400">
                {chatError}
              </div>
            )}

            {/* Input */}
            <form
              onSubmit={handleSendMessage}
              className="border-t border-slate-100 dark:border-slate-800 px-6 py-4 flex items-center gap-3"
            >
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                placeholder={t.typePlaceholder}
                className="flex-1 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#0B3B60]/20 focus:border-[#0B3B60] transition-all"
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isTyping}
                className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-r from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6] text-white
                           hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed
                           transition-all duration-200 shadow-sm"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </form>
          </div>
        )}

        {/* NOTES TAB */}
        {activeTab === 'notes' && (
          <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">{t.tabNotes}</h2>
              <span className="text-xs text-slate-500 dark:text-slate-400">{t.autoSaved}</span>
            </div>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder={t.notesPlaceholder}
              className="w-full min-h-[400px] p-4 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-100
                         focus:outline-none focus:ring-2 focus:ring-[#0B3B60]/20 focus:border-[#0B3B60]
                         transition-all resize-y leading-relaxed placeholder:text-slate-300 dark:placeholder:text-slate-600"
            />
            <div className="flex items-center justify-between mt-3">
              <div className="text-xs text-slate-400 dark:text-slate-500">{notes.length} {t.characters}</div>
              <button
                onClick={() => { setNotes(''); localStorage.removeItem(STORAGE_KEY_NOTES) }}
                className="text-xs text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 px-3 py-1.5 rounded-lg transition-colors"
              >
                {t.clearNotes}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
