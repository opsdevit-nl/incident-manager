// src/lib/filters.js
import { writable } from 'svelte/store';

export const filters = writable({
  statusFilter: 'open',
  teamFilter: '',
  assigneeFilter: '',
  severityFilter: '',
  sortBy: 'created',
  sortOrder: 'desc'
});