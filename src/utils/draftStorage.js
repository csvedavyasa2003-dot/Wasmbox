const STORAGE_KEY = "wasmbox-draft"

export function saveDraft(code, title) {
  const draft = {
    code,
    title,
  }

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(draft)
  )
}

export function loadDraft() {
  const savedDraft = localStorage.getItem(STORAGE_KEY)

  if (!savedDraft) {
    return null
  }

  try {
    return JSON.parse(savedDraft)
  } catch {
    return null
  }
}

export function clearDraft() {
  localStorage.removeItem(STORAGE_KEY)
}
