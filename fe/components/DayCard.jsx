"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useApp } from '../context/AppContext'

// Map of slide files per day – mirrors the data/slides folder
const SLIDE_FILES = {
  '01': [
    { name: 'd1-slide-hackathon.pdf', file: '/slides/d1-slide-hackathon.pdf' },
  ],
  '02': [
    { name: 'd2-slide-hackathon.pdf', file: '/slides/d2-slide-hackathon.pdf' },
  ],
}

function DownloadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function FileIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0 text-slate-400 dark:text-slate-500">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

export default function DayCard({ day, onToggle }){
  const router = useRouter()
  const [open, setOpen] = useState(day.seq === '01' || day.seq === '1')
  const { lang } = useApp()
  const isVi = lang === 'VI'

  const t = {
    notCompleted: isVi ? 'Chưa hoàn thành ngày học' : 'Learning day incomplete',
    completed: isVi ? 'Đã hoàn thành ngày học' : 'Learning day completed',
    slidesCount: isVi ? 'slide' : 'slides',
    download: isVi ? 'Tải xuống' : 'Download',
    downloadAll: isVi ? 'Tải tất cả slide' : 'Download all slides',
  }

  const slides = SLIDE_FILES[day.seq] || Array.from({ length: day.slides }, (_, i) => ({
    name: `slide_${i + 1}.pdf`,
    file: '#'
  }))

  function handleDownload(e, slide) {
    e.stopPropagation()
    const link = document.createElement('a')
    link.href = slide.file
    link.download = slide.name
    link.click()
  }

  function handleOpenFile(slide) {
    router.push(`/reader?file=${slide.name}&day=${day.seq}`)
  }

  return (
    <div className="bg-white dark:bg-[#1E293B] border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md">
      {/* Header row – always visible */}
      <div
        className="flex items-center p-5 cursor-pointer select-none"
        onClick={() => setOpen(!open)}
      >
        {/* Day badge */}
        <div className="w-20 flex-shrink-0">
          <div className="bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/80 rounded-2xl w-[68px] h-[68px] flex flex-col items-center justify-center">
            <div className="text-[10px] font-bold tracking-widest text-[#E11D48] dark:text-rose-400 uppercase">DAY</div>
            <div className="font-extrabold text-2xl text-slate-900 dark:text-white leading-none mt-0.5">{day.seq}</div>
          </div>
        </div>

        {/* Title & meta */}
        <div className="flex-1 pl-4">
          <div className="text-base font-bold text-slate-900 dark:text-white">{day.title}</div>
          <div className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            {day.is_completed ? t.completed : t.notCompleted} · {day.slides} {t.slidesCount}
          </div>
        </div>

        {/* Chevron */}
        <div className="w-10 flex items-center justify-center">
          <svg
            width="20" height="20" viewBox="0 0 24 24" fill="none"
            className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          >
            <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400 dark:text-slate-500"/>
          </svg>
        </div>
      </div>

      {/* Slide list – expanded */}
      {open && (
        <div className="border-t border-slate-100 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-800/30">
          {slides.map((slide, i) => (
            <div
              key={i}
              onClick={() => handleOpenFile(slide)}
              className="flex items-center justify-between px-6 py-3.5 group hover:bg-blue-50/60 dark:hover:bg-slate-800/80 transition-all cursor-pointer border-l-4 border-transparent hover:border-[#0B3B60] dark:hover:border-[#38BDF8]"
              style={{ borderBottom: i < slides.length - 1 ? '1px solid var(--tw-border-slate)' : 'none' }}
            >
              {/* File info */}
              <div className="flex items-center gap-3">
                <FileIcon />
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 group-hover:text-[#0B3B60] dark:group-hover:text-[#38BDF8] transition-colors">{slide.name}</span>
              </div>

              {/* Download button */}
              <button
                onClick={(e) => handleDownload(e, slide)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium
                           text-[#0B3B60] dark:text-[#38BDF8] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700
                           hover:bg-[#0B3B60] hover:text-white dark:hover:bg-[#38BDF8] dark:hover:text-slate-900
                           transition-all duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100 shadow-sm"
                title={`Tải ${slide.name}`}
              >
                <DownloadIcon />
                <span>{t.download}</span>
              </button>
            </div>
          ))}


          {/* Download all button */}
          <div className="px-6 py-3 border-t border-slate-100 dark:border-slate-800">
            <button
              onClick={(e) => {
                e.stopPropagation()
                slides.forEach(slide => {
                  const link = document.createElement('a')
                  link.href = slide.file
                  link.download = slide.name
                  link.click()
                })
              }}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold
                         text-white bg-gradient-to-r from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#3B82F6]
                         hover:from-[#0a3050] hover:to-[#1255a0]
                         transition-all duration-200 shadow-sm hover:shadow"
            >
              <DownloadIcon />
              <span>{t.downloadAll} ({slides.length})</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
