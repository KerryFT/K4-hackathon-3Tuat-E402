const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'
const CONVERSATION_STORAGE_KEY = 'vlearn_conversation_id'

let memoryConversationId = null

function createConversationId() {
  if (typeof globalThis.crypto?.randomUUID === 'function') {
    return globalThis.crypto.randomUUID()
  }
  return `vlearn-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function persistConversationId(conversationId) {
  memoryConversationId = conversationId
  try {
    globalThis.sessionStorage?.setItem(CONVERSATION_STORAGE_KEY, conversationId)
  } catch {}
  return conversationId
}

export function getOrCreateConversationId() {
  if (memoryConversationId) return memoryConversationId

  try {
    const savedId = globalThis.sessionStorage?.getItem(CONVERSATION_STORAGE_KEY)
    if (savedId) return persistConversationId(savedId)
  } catch {}

  return persistConversationId(createConversationId())
}

export function resetConversationSession() {
  return persistConversationId(createConversationId())
}

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`)
  }
  return response.json()
}

export function getCourseInfo() {
  return request('/course/info')
}

export function getCourseDays() {
  return request('/course/days')
}

export function toggleDay(id) {
  return request(`/course/toggle-day/${id}`, { method: 'POST' })
}

export async function sendChatMessage(payload) {
  const conversationId = payload.conversation_id || getOrCreateConversationId()
  const response = await request('/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...payload,
      conversation_id: conversationId,
    }),
  })
  if (response.conversation_id) {
    persistConversationId(response.conversation_id)
  }
  return response
}
