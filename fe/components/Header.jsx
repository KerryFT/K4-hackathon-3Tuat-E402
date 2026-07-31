"use client"
import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useApp } from '../context/AppContext'

export default function Header({ onStart }) {
  const pathname = usePathname()
  const router = useRouter()
  const { lang, toggleLang, dark, toggleDark, user, logout } = useApp()
  const [openUser, setOpenUser] = useState(false)
  const popupRef = useRef(null)

  // Close popup when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (popupRef.current && !popupRef.current.contains(event.target)) {
        setOpenUser(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const isHome = pathname === '/' || pathname === '/home'
  const isCourses = pathname === '/my-courses'
  const isNotebook = pathname === '/notebook'
  const isProfile = pathname === '/profile'
  const showNotebook = isCourses || isNotebook

  const t = {
    home: lang === 'VI' ? 'Trang chủ' : 'Home',
    myCourses: lang === 'VI' ? 'Khóa học của tôi' : 'My Courses',
    notebook: lang === 'VI' ? 'Sổ tay học tập' : 'Learning Notebook',
    openCodelabs: lang === 'VI' ? 'Mở Codelabs' : 'Open Codelabs',
    vlearnAccount: lang === 'VI' ? 'TÀI KHOẢN VLEARN' : 'VLEARN ACCOUNT',
    role: lang === 'VI' ? 'Vai trò' : 'Role',
    cohort: lang === 'VI' ? 'Cohort' : 'Cohort',
    viewProfileAndSubmissions: lang === 'VI' ? 'Xem hồ sơ và bài đã nộp' : 'View profile & submissions',
    logout: lang === 'VI' ? 'Đăng xuất' : 'Log out',
  }

  const handleLogoutClick = () => {
    setOpenUser(false)
    logout()
    router.push('/logout')
  }

  const handleProfileClick = () => {
    setOpenUser(false)
    router.push('/profile')
  }

  return (
    <header className="w-full bg-white dark:bg-[#1E293B] border-b border-slate-200 dark:border-slate-700/80 transition-colors duration-200 sticky top-0 z-40">
      <div className="container-centered flex items-center justify-between py-2.5 sm:py-3 gap-2 sm:gap-4">
        <div className="flex items-center gap-2 sm:gap-6 md:gap-8 min-w-0">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
            <div className="w-8 h-8 flex items-center justify-center">
              <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden>
                <path d="M4 16L16 4L28 16" stroke="#E11D48" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M4 16L16 28L28 16" stroke={dark ? "#38BDF8" : "#0B3B60"} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="font-extrabold text-slate-900 dark:text-white text-base sm:text-lg tracking-tight">VLearn</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-0.5 sm:gap-1 text-xs sm:text-sm overflow-x-auto no-scrollbar">
            <Link
              href="/"
              className={`flex items-center gap-1.5 px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg transition-colors font-medium whitespace-nowrap ${
                isHome
                  ? 'text-[#0B3B60] dark:text-[#38BDF8] font-semibold bg-slate-100 dark:bg-slate-800'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <span>{t.home}</span>
            </Link>

            <Link
              href="/my-courses"
              className={`flex items-center gap-1.5 px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg transition-colors font-medium whitespace-nowrap ${
                isCourses
                  ? 'text-[#0B3B60] dark:text-[#38BDF8] font-semibold bg-slate-100 dark:bg-slate-800'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
              <span>{t.myCourses}</span>
            </Link>

            {/* Sổ tay học tập */}
            {showNotebook && (
              <Link
                href="/notebook"
                className={`flex items-center gap-1.5 px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg transition-colors font-medium whitespace-nowrap ${
                  isNotebook
                    ? 'text-[#0B3B60] dark:text-[#38BDF8] font-semibold bg-slate-100 dark:bg-slate-800'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                  <line x1="8" y1="7" x2="16" y2="7"/>
                  <line x1="8" y1="11" x2="14" y2="11"/>
                </svg>
                <span>{t.notebook}</span>
              </Link>
            )}
          </nav>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 flex-shrink-0">
          {/* 1. Mở Codelabs -> https://codelabs.vlearn.dev/codelab */}
          <a
            href="https://codelabs.vlearn.dev/codelab"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-2.5 py-1.5 sm:px-3.5 sm:py-2 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="text-slate-500 dark:text-slate-400">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            <span className="hidden sm:inline">{t.openCodelabs}</span>
          </a>

          {/* 2. Language toggle VI / EN */}
          <button
            onClick={toggleLang}
            className="px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-xs sm:text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm"
            title="Đổi ngôn ngữ / Change language"
          >
            {lang}
          </button>

          {/* 3. Dark mode toggle */}
          <button
            onClick={toggleDark}
            className="p-1.5 sm:p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm"
            title={dark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
          >
            {dark ? (
              /* Sun icon for light mode */
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="sm:w-[18px] sm:h-[18px]">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            ) : (
              /* Moon icon for dark mode */
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="sm:w-[18px] sm:h-[18px]">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            )}
          </button>

          {/* 4. User account popup */}
          <div className="relative" ref={popupRef}>
            <button
              onClick={() => setOpenUser(!openUser)}
              className="flex items-center gap-1.5 sm:gap-2.5 px-2 py-1 sm:px-3 sm:py-1.5 border border-slate-200 dark:border-slate-700 rounded-full hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm"
            >
              <div className="bg-slate-100 dark:bg-slate-700 text-[#0B3B60] dark:text-[#38BDF8] w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-xs font-bold">
                {user.avatarChar}
              </div>
              <div className="hidden md:block text-sm text-slate-700 dark:text-slate-200 max-w-[160px] truncate font-medium">
                {user.shortEmail}
              </div>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`text-slate-400 transition-transform duration-200 ${openUser ? 'rotate-180' : ''}`}>
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </button>

            {/* Popup matching exact design from image */}
            {openUser && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-[#1E293B] border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl p-5 z-50 animate-in fade-in duration-150">
                {/* Popup header */}
                <div className="text-[11px] font-bold text-slate-400 dark:text-slate-400 tracking-wider uppercase">
                  {t.vlearnAccount}
                </div>
                <div className="text-base font-extrabold text-slate-900 dark:text-white mt-1 break-all">
                  {user.email}
                </div>

                {/* Info rows */}
                <div className="mt-4 space-y-2 text-sm border-t border-b border-slate-100 dark:border-slate-800 py-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400 font-medium">{t.role}</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{user.role}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400 font-medium">{t.cohort}</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{user.cohort}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-4 space-y-2.5">
                  {/* Button 1: Xem hồ sơ và bài đã nộp */}
                  <button
                    onClick={handleProfileClick}
                    className="w-full flex items-center justify-center gap-2.5 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-bold text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-colors shadow-sm group"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-600 dark:text-slate-300 group-hover:scale-105 transition-transform">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                    <span>{t.viewProfileAndSubmissions}</span>
                  </button>

                  {/* Button 2: Đăng xuất */}
                  <button
                    onClick={handleLogoutClick}
                    className="w-full flex items-center justify-center gap-2.5 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-bold text-slate-700 dark:text-slate-200 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 dark:hover:text-red-400 hover:border-red-200 dark:hover:border-red-800/50 transition-colors shadow-sm group"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-600 dark:text-slate-300 group-hover:text-red-500 transition-colors">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                      <polyline points="16 17 21 12 16 7"/>
                      <line x1="21" y1="12" x2="9" y2="12"/>
                    </svg>
                    <span>{t.logout}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
