// src/lib/filters.js
import { writable } from 'svelte/store';

// export const filters = writable({
//   statusFilter: 'open',
//   teamFilter: '',
//   assigneeFilter: '',
//   severityFilter: '',
//   sortBy: 'created',
//   sortOrder: 'desc',
//   firstAlertStart: '',
//   firstAlertEnd: '',
//   lastAlertStart: '',
//   lastAlertEnd: ''
// });

import { browser } from '$app/environment';

export const FILTER_PREF_KEY = "filterPreferences";

export function loadFilterPreferences() {
  if (!browser) {
    return {
      statusFilter: 'open',
      teamFilter: '',
      assigneeFilter: '',
      severityFilter: '',
      sortBy: 'created',
      sortOrder: 'desc',
      firstAlertStart: '',
      firstAlertEnd: '',
      lastAlertStart: '',
      lastAlertEnd: ''
    };
  }
  try {
    const pref = localStorage.getItem(FILTER_PREF_KEY);
    if (pref) {
      return JSON.parse(pref);
    }
  } catch (err) {
    console.error("Error loading filter preferences:", err);
  }
  return {
    statusFilter: 'open',
    teamFilter: '',
    assigneeFilter: '',
    severityFilter: '',
    sortBy: 'created',
    sortOrder: 'desc',
    firstAlertStart: '',
    firstAlertEnd: '',
    lastAlertStart: '',
    lastAlertEnd: ''
  };
}

export function saveFilterPreferences(f) {
  if (!browser) return;
  try {
    localStorage.setItem(FILTER_PREF_KEY, JSON.stringify(f));
  } catch (err) {
    console.error("Error saving filter preferences:", err);
  }
}