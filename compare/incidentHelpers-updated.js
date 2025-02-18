import { browser } from '$app/environment';

export const PREF_KEY = "incidentPreferences";

export function loadPreferences() {
  if (!browser) {
    return { 
      allCollapsed: true, 
      collapsed: {}, 
      allCommentsCollapsed: true, 
      allMainAlertsCollapsed: true, 
      mainAlertsCollapsed: {},
      darkMode: false
    };
  }
  try {
    const pref = localStorage.getItem(PREF_KEY);
    if (pref) {
      let p = JSON.parse(pref);
      if (p.darkMode === undefined) p.darkMode = false;
      return p;
    }
  } catch (err) {
    console.error("Error loading preferences:", err);
  }
  return { 
    allCollapsed: true, 
    collapsed: {}, 
    allCommentsCollapsed: true, 
    allMainAlertsCollapsed: true, 
    mainAlertsCollapsed: {},
    darkMode: false
  };
}

export function savePreferences(p) {
  if (!browser) return;
  try {
    localStorage.setItem(PREF_KEY, JSON.stringify(p));
  } catch (err) {
    console.error("Error saving preferences:", err);
  }
}

export async function fetchIncidents(
  statusFilter,
  teamFilter,
  assigneeFilter,
  severityFilter,
  allIncidentsCollapsed,
  allMainAlertsCollapsed,
  allCommentsCollapsed,
  prefs
) {
  // Append a timestamp parameter to avoid caching issues.
  const url = new URL("http://localhost:8000/incidents");
  url.searchParams.append("status", statusFilter);
  if (teamFilter) url.searchParams.append("team", teamFilter);
  if (assigneeFilter) url.searchParams.append("assignee", assigneeFilter);
  if (severityFilter) url.searchParams.append("severity", severityFilter);
  url.searchParams.append("t", Date.now());
  
  const response = await fetch(url.toString());
  let incidents = await response.json();
  incidents.forEach(inc => {
    inc.renameText = inc.incident_name;
    inc.newCommentLogin = "";
    inc.newCommentText = "";
    inc.editingComment = null;
    inc.showCommentEditor = false;
    inc.selectedForBulk = inc.selectedForBulk || false;
    inc.collapsed = (prefs.collapsed[inc.id] !== undefined)
                      ? prefs.collapsed[inc.id]
                      : allIncidentsCollapsed;
    inc.showMainAlerts = (prefs.mainAlertsCollapsed[inc.id] !== undefined)
                         ? !prefs.mainAlertsCollapsed[inc.id]
                         : !allMainAlertsCollapsed;
    inc.showComments = !allCommentsCollapsed;
    inc.draggable = true;
    if (inc.showSeverityDropdown === undefined) inc.showSeverityDropdown = false;
    if (inc.showTeamDropdown === undefined) inc.showTeamDropdown = false;
    if (inc.showAssigneeDropdown === undefined) inc.showAssigneeDropdown = false;
    if (inc.editingTitle === undefined) inc.editingTitle = false;
    if (inc.comments) {
      inc.comments.forEach(comment => {
        comment.editText = comment.comment_text;
      });
    }
    if (inc.main_alerts) {
      inc.main_alerts.forEach(ma => {
        ma.selectedForBulk = false;
        ma.draggable = true;
      });
    }
  });
  return incidents;
}
