'use client';
import Header from '../components/Header'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { getCourseInfo } from '../utils/api'
import { useApp } from '../context/AppContext'

export default function HomePage() {
  const [info, setInfo] = useState(null)
  const { lang, user } = useApp()

  useEffect(() => {
    getCourseInfo()
      .then(data => setInfo(data))
      .catch(() => {})
  }, [])

  const isVi = lang === 'VI'
  const totalCourses = 1
  const totalQuestions = 13
  const daysRead = info?.progress_completed ?? 0
  const daysTotal = info?.progress_total ?? 6

  const t = {
    subHeading: isVi ? 'VLEARN · VINUNI AI THỰC CHIẾN' : 'VLEARN · VINUNI PRACTICAL AI',
    title: isVi ? 'Không gian học tập VLearn' : 'VLearn Learning Workspace',
    description: isVi
      ? 'Theo dõi tiến độ, học liệu và phần kiến thức cần củng cố tại VinUni AI Thực Chiến.'
      : 'Track your progress, learning materials, and knowledge points at VinUni Practical AI.',
    coursesCount: isVi ? `${totalCourses} khóa học đang theo học` : `${totalCourses} enrolled course`,
    welcomeTitle: isVi ? `Chào mừng trở lại, ${user?.name || 'VŨ HỮU TRƯỜNG'}!` : `Welcome back, ${user?.name || 'VŨ HỮU TRƯỜNG'}!`,
    welcomeDesc: isVi
      ? 'VLearn đang tổng hợp tiến độ đọc và các tín hiệu học tập. Mở Khóa học của tôi để tiếp tục ngày học hoặc trao đổi cùng VLearn Tutor.'
      : 'VLearn is aggregating your reading progress and learning signals. Open My Courses to continue your learning day or chat with VLearn Tutor.',
    learningSignal: isVi ? 'Tín hiệu học tập đang hoạt động' : 'Active learning signal',
    readDays: isVi ? `Đã đọc ${daysRead}/${daysTotal} ngày học` : `Read ${daysRead}/${daysTotal} learning days`,
    coursesCard: isVi ? 'Khóa học' : 'Courses',
    questionsCard: isVi ? 'Câu hỏi với tutor' : 'Questions with tutor',
    viewMyCourses: isVi ? 'Xem khóa học của tôi' : 'View my courses',
    viewMyCoursesDesc: isVi ? 'Mở danh sách đầy đủ các lớp bạn đang theo học.' : 'Open the full list of classes you are currently enrolled in.'
  }

  return (
    <div className="min-h-screen bg-[#F1F5F9] dark:bg-[#0F172A] transition-colors duration-200">
      <Header />

      {/* Top banner */}
      <div className="bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="container-centered py-4 sm:py-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
          <div>
            <div className="text-xs font-bold text-[#E11D48] tracking-wider uppercase">
              {t.subHeading}
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white mt-1">
              {t.title}
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
              {t.description}
            </p>
          </div>
          <Link
            href="/my-courses"
            className="self-start sm:self-auto flex items-center gap-2 px-3.5 py-2 sm:px-4 sm:py-2.5 border border-slate-200 dark:border-slate-700 rounded-full text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors whitespace-nowrap shadow-xs"
          >
            <span className="text-[#0B3B60] dark:text-[#38BDF8] font-semibold">{t.coursesCount}</span>
          </Link>
        </div>
      </div>

      {/* Main content */}
      <main className="container-centered py-4 sm:py-6 space-y-5">
        {/* Welcome card */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0B3B60] to-[#1565A8] dark:from-[#1E3A8A] dark:to-[#0F4C81] shadow-md" style={{minHeight: '180px'}}>
          {/* Decorative red accent */}
          <div className="absolute top-0 right-0 w-[120px] h-full pointer-events-none">
            <svg viewBox="0 0 120 180" fill="none" className="w-full h-full" preserveAspectRatio="none">
              <path d="M20 0H120V180H0L20 0Z" fill="#CC1B38" opacity="0.85" />
            </svg>
          </div>

          <div className="relative z-10 p-5 sm:p-8">
            <div className="text-xs font-bold text-blue-200 tracking-wider uppercase">
              {t.subHeading}
            </div>
            <h2 className="text-2xl font-extrabold text-white mt-3">
              {t.welcomeTitle}
            </h2>
            <p className="text-sm text-blue-100 mt-2 max-w-xl leading-relaxed">
              {t.welcomeDesc}
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-5">
              <span className="inline-flex items-center gap-1.5 bg-white/15 backdrop-blur-sm text-white text-xs font-medium px-3 py-1.5 rounded-full border border-white/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
                {t.learningSignal}
              </span>
              <span className="inline-flex items-center gap-1.5 bg-white/15 backdrop-blur-sm text-white text-xs font-medium px-3 py-1.5 rounded-full border border-white/20">
                {t.readDays}
              </span>
            </div>
          </div>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Courses count */}
          <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-5 flex items-center gap-4 transition-colors">
            <div className="w-11 h-11 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="text-slate-600 dark:text-slate-300">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.coursesCard}</div>
              <div className="text-2xl font-extrabold text-slate-900 dark:text-white mt-0.5">{totalCourses}</div>
            </div>
          </div>

          {/* Questions count */}
          <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-5 flex items-center gap-4 transition-colors">
            <div className="w-11 h-11 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="text-slate-600 dark:text-slate-300">
                <path d="M9 18l6-6-6-6"/>
                <path d="M15 18l-6-6 6-6" transform="translate(4, 0)"/>
              </svg>
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.questionsCard}</div>
              <div className="text-2xl font-extrabold text-slate-900 dark:text-white mt-0.5">{totalQuestions}</div>
            </div>
          </div>
        </div>

        {/* View my courses link card */}
        <Link href="/my-courses" className="block">
          <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-5 flex items-center justify-between group hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md transition-all cursor-pointer">
            <div className="flex items-center gap-4">
              <div className="w-11 h-11 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="text-[#0B3B60] dark:text-[#38BDF8]">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
              </div>
              <div>
                <div className="text-base font-bold text-slate-900 dark:text-white">{t.viewMyCourses}</div>
                <div className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{t.viewMyCoursesDesc}</div>
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-slate-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-slate-100 dark:group-hover:bg-slate-700 transition-colors flex-shrink-0">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-slate-600 dark:text-slate-300">
                <path d="M9 5l7 7-7 7"/>
              </svg>
            </div>
          </div>
        </Link>
      </main>
    </div>
  )
}
