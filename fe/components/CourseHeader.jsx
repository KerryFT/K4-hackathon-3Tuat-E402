'use client'
import { useApp } from '../context/AppContext'

import { useRouter } from 'next/navigation'

export default function CourseHeader({ info, progressPercent = 0, onStart }) {
  const router = useRouter()
  const { lang } = useApp()
  const isVi = lang === 'VI'

  const t = {
    sub: isVi ? 'VLEARN · VINUNI AI THỰC CHIẾN' : 'VLEARN · VINUNI PRACTICAL AI',
    defaultTitle: isVi ? 'COMP2010 - Khoá 3 + 4 Phase 1' : 'COMP2010 - Cohort 3 + 4 Phase 1',
    students: isVi ? 'học viên cùng lớp' : 'classmates enrolled',
    readDays: isVi ? 'Đã đọc' : 'Read',
    days: isVi ? 'ngày' : 'days',
    startReading: isVi ? 'Bắt đầu đọc' : 'Start Reading',
  }

  function handleStartReading(e) {
    if (onStart) onStart(e)
    router.push('/reader?file=day01_302.pdf&day=01')
  }

  return (
    <div className="bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="container-centered flex flex-col md:flex-row md:items-center justify-between py-6 gap-4">
        <div>
          <div className="text-xs font-bold text-red-600 dark:text-red-500 tracking-wider">
            {t.sub}
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white mt-2">
            {info?.title ?? t.defaultTitle}
          </h2>
          <div className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {info?.students ?? 1074} {t.students}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="bg-slate-50 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700/60 rounded-xl p-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-slate-100">
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">✓</span> {t.readDays} {info?.progress_completed ?? 0}/{info?.progress_total ?? 6} {t.days}
            </div>
            <div className="w-40 bg-slate-200 dark:bg-slate-700 h-2 rounded mt-2 overflow-hidden">
              <div className="h-2 rounded transition-all duration-300 bg-[#0B3B60] dark:bg-[#38BDF8]" style={{ width: `${progressPercent}%` }}></div>
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{progressPercent}%</div>
          </div>

          <button
            onClick={handleStartReading}
            className="px-6 py-2.5 bg-[#0B3B60] dark:bg-[#1E3A8A] hover:bg-[#0a3050] dark:hover:bg-[#1e40af] text-white rounded-full font-semibold transition-all shadow-sm hover:shadow"
          >
            {t.startReading}
          </button>
        </div>
      </div>
    </div>
  )
}
