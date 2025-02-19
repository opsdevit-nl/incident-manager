<script>
  import QuillEditor from "$lib/QuillEditor.svelte";
  import { onMount, getContext } from "svelte";
  import { loadFilterPreferences, saveFilterPreferences } from '$lib/filters.js';
  import { fetchIncidents, loadPreferences, savePreferences } from "$lib/incidentHelpers.js";
  import { browser } from '$app/environment';
  import io from 'socket.io-client';
  import { get } from 'svelte/store';

  // Retrieve the shared undo manager and incidents store.
  const { recordAction } = getContext("undoManager");
  const incidentsStore = getContext("incidentsStore");
  const filtersStore = getContext("filters");

  // Local state defaults
  let newAlertName = "";
  let bulkTargetIncidentId = "";

  // Global collapse states – default values
  let allIncidentsCollapsed = true;
  let allMainAlertsCollapsed = true;
  let allCommentsCollapsed = true;

  // NEW: Global view mode – compact view toggle
  let compactView = false;

  // --------------------------------------------
  // NEW: Column Visibility
  // --------------------------------------------
  // We define defaults for each column's visibility:
  let defaultColumnVisibility = {
  id: true,
  first_alert: true,
  last_alert: true,
  host: true,
  title: true,
  status: true,
  severity: true,
  team: true,
  assignee: true,
  source: true,
  state: true,
  alerts: true
};


  // A local store for whether the user is showing the "Customize Columns" menu
  let showColumnSettings = false;

  // Load preferences from local storage
  let prefs = loadPreferences();

  // If no columnVisibility object in prefs, create it from defaults:
  if (!prefs.columnVisibility) {
    prefs.columnVisibility = { ...defaultColumnVisibility };
    savePreferences(prefs);
  }

  // Create a reactive local copy for binding checkboxes:
  let columnVisibility = { ...prefs.columnVisibility };

  function toggleColumn(columnKey) {
    columnVisibility[columnKey] = !columnVisibility[columnKey];
    prefs.columnVisibility = columnVisibility;
    savePreferences(prefs);
  }
  // --------------------------------------------

  // Ensure the object for comment collapse is present.
  if (!prefs.commentsCollapsed) {
    prefs.commentsCollapsed = {};
  }

  onMount(() => {
    if (browser) {
      // Read collapse preferences
      allIncidentsCollapsed = localStorage.getItem("allIncidentsCollapsed") !== "false";
      allMainAlertsCollapsed = localStorage.getItem("allMainAlertsCollapsed") !== "false";
      allCommentsCollapsed = localStorage.getItem("allCommentsCollapsed") !== "false";
      // Read compact view preference (default false)
      compactView = localStorage.getItem("compactView") === "true";
    }
    setTimeout(() => {
      fetchIncidentsWrapper();
    }, 0);

    const handleClickOutside = (event) => {
    // If the menu is open and the clicked element is not inside the column-settings-container, close the menu.
    if (showColumnSettings && !event.target.closest('.column-settings-container')) {
      showColumnSettings = false;
    }
  };

  window.addEventListener('click', handleClickOutside);
  
  return () => {
    window.removeEventListener('click', handleClickOutside);
  };

    let socket;
    // Connect to your Socket.IO server (ensure the URL is correct)
    socket = io("http://localhost:8000/", { path: "/socket.io" });

    // Listen for "incident_update" events and refresh incidents on receipt
    socket.on("incident_update", (data) => {
      console.log("Received update via socket:", data);
      fetchIncidentsWrapper();
    });

    return () => {
      socket.disconnect();
    }
  });

  // Reactive block guarded by browser condition to avoid SSR fetches.
  $: if (browser) {
    $filtersStore;
    fetchIncidentsWrapper();
  }

$: {
  prefs.columnVisibility = columnVisibility;
  savePreferences(prefs);
}

  async function fetchIncidentsWrapper() {
    const f = get(filtersStore);
    let data = await fetchIncidents(
      f.statusFilter,
      f.teamFilter,
      f.assigneeFilter,
      f.severityFilter,
      allIncidentsCollapsed,
      allMainAlertsCollapsed,
      allCommentsCollapsed,
      prefs,
      f.firstAlertStart,
      f.firstAlertEnd,
      f.lastAlertStart,
      f.lastAlertEnd
    );

    // --- Date/time filtering for first_alert_time ---
    if (f.firstAlertStart && !isNaN(new Date(f.firstAlertStart).getTime())) {
      let startDate = new Date(f.firstAlertStart);
      // Convert local time to UTC
      startDate = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000);
      data = data.filter(inc => {
        let incidentDate = new Date(inc.first_alert_time + "Z");
        return incidentDate >= startDate;
      });
    }
    if (f.firstAlertEnd && !isNaN(new Date(f.firstAlertEnd).getTime())) {
      let endDate = new Date(f.firstAlertEnd);
      endDate = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000);
      data = data.filter(inc => {
        let incidentDate = new Date(inc.first_alert_time + "Z");
        return incidentDate <= endDate;
      });
    }

    // --- Date/time filtering for last_alert_time ---
    if (f.lastAlertStart && !isNaN(new Date(f.lastAlertStart).getTime())) {
      let startDate = new Date(f.lastAlertStart);
      startDate = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000);
      data = data.filter(inc => {
        if (!inc.last_alert_time) return false;
        let incidentDate = new Date(inc.last_alert_time + "Z");
        return incidentDate >= startDate;
      });
    }
    if (f.lastAlertEnd && !isNaN(new Date(f.lastAlertEnd).getTime())) {
      let endDate = new Date(f.lastAlertEnd);
      endDate = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000);
      data = data.filter(inc => {
        if (!inc.last_alert_time) return false;
        let incidentDate = new Date(inc.last_alert_time + "Z");
        return incidentDate <= endDate;
      });
    }

    // --- Sorting ---
    if (f.sortBy) {
      data.sort((a, b) => {
        let compare = 0;
        switch (f.sortBy) {
          case 'alert_count':
            compare = a.alert_count - b.alert_count;
            break;
          case 'created':
            compare = new Date(a.id) - new Date(b.id);
            break;
          case 'last_alert':
            compare = new Date(a.last_alert_time) - new Date(b.last_alert_time);
            break;
          case 'team':
            compare = a.team.localeCompare(b.team);
            break;
          case 'severity':
            const severityOrder = { 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'MAJOR': 4 };
            compare = (severityOrder[a.severity] || 0) - (severityOrder[b.severity] || 0);
            break;
          default:
            compare = 0;
        }
        return f.sortOrder === 'desc' ? -compare : compare;
      });
    }
  // Merge each incident’s collapsed and expandedOverride states from your local prefs.
  data = data.map(inc => ({
    ...inc,
    collapsed: (prefs.collapsed && prefs.collapsed[inc.id] !== undefined)
      ? prefs.collapsed[inc.id]
      : allIncidentsCollapsed,
    expandedOverride: (prefs.expandedOverride && prefs.expandedOverride[inc.id] !== undefined)
      ? prefs.expandedOverride[inc.id]
      : false
  }));
    incidentsStore.set([...data]);
    console.log("Fetched and sorted incidents:", data);
  }

  // Save functions
  function saveIncidentPreference(incidentId, collapsed) {
    prefs.collapsed[incidentId] = collapsed;
    savePreferences(prefs);
  }
  function saveMainAlertsPreference(incidentId, collapsed) {
    prefs.mainAlertsCollapsed[incidentId] = collapsed;
    savePreferences(prefs);
  }
  function saveCommentsPreference(incidentId, collapsed) {
    prefs.commentsCollapsed[incidentId] = collapsed;
    savePreferences(prefs);
  }

  // UI-only toggle functions (without re-fetching)
  function toggleIncidentCollapse(inc) {
    incidentsStore.update(items =>
      items.map(item =>
        item.id === inc.id ? { ...item, collapsed: !item.collapsed } : item
      )
    );
    const newVal = !inc.collapsed;
    prefs.collapsed[inc.id] = newVal;
    savePreferences(prefs);
  }

  function toggleMainAlerts(inc) {
    let newVal;
    incidentsStore.update(items =>
      items.map(item => {
        if (item.id === inc.id) {
          newVal = !item.showMainAlerts;
          return { ...item, showMainAlerts: newVal };
        }
        return item;
      })
    );
    saveMainAlertsPreference(inc.id, !newVal);
  }

  function toggleComments(inc) {
    let newVal;
    incidentsStore.update(items =>
      items.map(item => {
        if (item.id === inc.id) {
          newVal = !item.showComments;
          return { ...item, showComments: newVal };
        }
        return item;
      })
    );
    saveCommentsPreference(inc.id, !newVal);
  }

  // For dropdowns, ensure that opening one closes the others.
  const dropdownFields = ["Status", "Severity", "Team", "Assignee"];
  function toggleDropdown(inc, field) {
    dropdownFields.forEach(f => {
      if (f !== field) {
        inc["show" + f + "Dropdown"] = false;
      }
    });
    inc["show" + field + "Dropdown"] = !inc["show" + field + "Dropdown"];
    incidentsStore.update(items =>
      items.map(item =>
        item.id === inc.id
          ? {
              ...item,
              showStatusDropdown: inc.showStatusDropdown || false,
              showSeverityDropdown: inc.showSeverityDropdown || false,
              showTeamDropdown: inc.showTeamDropdown || false,
              showAssigneeDropdown: inc.showAssigneeDropdown || false
            }
          : item
      )
    );
  }

  function shortTimestamp(ts) {
    if (!ts) return "";
    const date = new Date(ts);
    // Format as MM/DD HH:MM
    const mm = ("0" + (date.getMonth() + 1)).slice(-2);
    const dd = ("0" + date.getDate()).slice(-2);
    const hh = ("0" + date.getHours()).slice(-2);
    const min = ("0" + date.getMinutes()).slice(-2);
  return `${mm}/${dd} ${hh}:${min}`;
}

  // Global toggles that re-fetch data.
  function toggleAllIncidents() {
    allIncidentsCollapsed = !allIncidentsCollapsed;
    prefs.allCollapsed = allIncidentsCollapsed;
    if (browser) {
      localStorage.setItem("allIncidentsCollapsed", allIncidentsCollapsed);
    }
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    $incidents.forEach(item => {
      prefs.collapsed[item.id] = allIncidentsCollapsed;
    });
    savePreferences(prefs);
    fetchIncidentsWrapper();
  }

  function toggleAllMainAlerts() {
    allMainAlertsCollapsed = !allMainAlertsCollapsed;
    if (!allMainAlertsCollapsed) {
      allIncidentsCollapsed = false;
      prefs.allCollapsed = false;
      if (browser) localStorage.setItem("allIncidentsCollapsed", "false");
    }
    prefs.allMainAlertsCollapsed = allMainAlertsCollapsed;
    if (browser) localStorage.setItem("allMainAlertsCollapsed", allMainAlertsCollapsed);
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    $incidents.forEach(item => {
      prefs.mainAlertsCollapsed[item.id] = allMainAlertsCollapsed;
      if (!allMainAlertsCollapsed) {
        prefs.collapsed[item.id] = false;
      }
    });
    savePreferences(prefs);
    fetchIncidentsWrapper();
  }

  function toggleAllComments() {
    allCommentsCollapsed = !allCommentsCollapsed;
    if (!allCommentsCollapsed) {
      allIncidentsCollapsed = false;
      prefs.allCollapsed = false;
      if (browser) localStorage.setItem("allIncidentsCollapsed", "false");
    }
    prefs.allCommentsCollapsed = allCommentsCollapsed;
    if (browser) localStorage.setItem("allCommentsCollapsed", allCommentsCollapsed);
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    $incidents.forEach(item => {
      prefs.commentsCollapsed[item.id] = allCommentsCollapsed;
      if (!allCommentsCollapsed) {
        prefs.collapsed[item.id] = false;
      }
    });
    savePreferences(prefs);
    fetchIncidentsWrapper();
  }

  // NEW: Global toggle for compact view.
  function toggleCompactView() {
    compactView = !compactView;
    if (browser) localStorage.setItem("compactView", compactView);
  }

  function toggleRowExpansion(inc) {
  inc.expandedOverride = !inc.expandedOverride;
  // Ensure prefs.expandedOverride exists
  prefs.expandedOverride = prefs.expandedOverride || {};
  prefs.expandedOverride[inc.id] = inc.expandedOverride;
  savePreferences(prefs);
  // Update the incident in the store
  incidentsStore.update(items =>
    items.map(item => item.id === inc.id ? { ...item, expandedOverride: inc.expandedOverride } : item)
  );
}

  // Toggle select/unselect all incidents.
  function toggleSelectAllIncidents() {
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    const allSelected = $incidents.every(item => item.selectedForBulk);
    incidentsStore.update(items =>
      items.map(item => ({ ...item, selectedForBulk: !allSelected }))
    );
  }

  function handleKeyAction(e, actionFn) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      actionFn();
    }
  }

  function formatTimestamp(ts) {
    const date = new Date(ts);
    const yyyy = date.getFullYear();
    const mm = ("0" + (date.getMonth() + 1)).slice(-2);
    const dd = ("0" + date.getDate()).slice(-2);
    const hh = ("0" + date.getHours()).slice(-2);
    const min = ("0" + date.getMinutes()).slice(-2);
    const ss = ("0" + date.getSeconds()).slice(-2);
    return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
  }

  function handleIncidentDragStart(event, incident) {
    event.dataTransfer.setData("application/incident", incident.id);
  }

  function handleIncidentDrop(event, targetIncidentId) {
    event.preventDefault();
    if (event.dataTransfer.types.includes("application/main-alert")) return;
    const sourceIncidentId = event.dataTransfer.getData("application/incident");
    if (sourceIncidentId && sourceIncidentId !== targetIncidentId.toString()) {
      fetch(`http://localhost:8000/incidents/${targetIncidentId}/drag_transfer/${sourceIncidentId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      }).then(() => fetchIncidentsWrapper());
    }
  }

  function handleMainAlertDragStart(event, mainAlert, fromIncidentId) {
    event.dataTransfer.setData("application/main-alert", JSON.stringify({ mainAlertId: mainAlert.id, fromIncidentId }));
  }

  async function handleMainAlertDrop(event, targetIncidentId) {
  event.preventDefault();
  event.stopPropagation();
  const data = event.dataTransfer.getData("application/main-alert");
  if (data) {
    const { mainAlertId, fromIncidentId } = JSON.parse(data);
    if (fromIncidentId !== targetIncidentId) {
      const response = await fetch(`http://localhost:8000/incidents/${targetIncidentId}/drag_link_main_alert/${mainAlertId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        // Update the collapsed state for both incidents to remain expanded.
        prefs.collapsed[fromIncidentId] = false;
        prefs.collapsed[targetIncidentId] = false;
        savePreferences(prefs);
        await fetchIncidentsWrapper();
      }
    }
  }
}

  function allowDrop(event) {
    event.preventDefault();
  }

  async function addIncidentComment(incidentId, loginName, commentText) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login_name: loginName, comment_text: commentText })
    });
    fetchIncidentsWrapper();
  }
  async function updateIncidentComment(incidentId, commentId, commentText) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/comments/${commentId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment_text: commentText })
    });
    fetchIncidentsWrapper();
  }
  async function submitComment(inc) {
    if (!inc.newCommentText) return;
    if (inc.editingComment) {
      await updateIncidentComment(inc.id, inc.editingComment.id, inc.newCommentText);
      fetchIncidentsWrapper();
      inc.editingComment = null;
    } else {
      await addIncidentComment(inc.id, inc.newCommentLogin, inc.newCommentText);
    }
    inc.newCommentText = "";
    inc.newCommentLogin = "";
    inc.showCommentEditor = false;
    fetchIncidentsWrapper();
  }
  function editComment(inc, comment) {
    inc.editingComment = comment;
    inc.newCommentText = comment.comment_text;
    inc.newCommentLogin = comment.login_name;
    inc.showCommentEditor = true;
    fetchIncidentsWrapper();
  }
  async function deleteIncidentComment(incidentId, commentId) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/comments/${commentId}`, {
      method: "DELETE"
    });
    fetchIncidentsWrapper();
  }

  async function createAlert() {
    if (!newAlertName) return;
    const response = await fetch("http://localhost:8000/alerts/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: newAlertName, state: 1, wikilink: "http://localhost:5000", host: "localhost", source: "pls"})
    });
    const data = await response.json();
    const incidentId = data.incident?.id || data.incident?.incident_id;
    console.log("Recording create action for incident", incidentId);
    if (incidentId !== undefined) {
      recordAction({ type: "create", alertName: newAlertName, alertId: data.alert.id, incidentId });
    } else {
      console.warn("No incident id returned in createAlert");
    }
    newAlertName = "";
    fetchIncidentsWrapper();
  }
  async function bulkReopenIncidents() {
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    const selectedIncidents = $incidents.filter(inc => inc.selectedForBulk && inc.status !== "open");
    for (const inc of selectedIncidents) {
      await fetch(`http://localhost:8000/incidents/${inc.id}/reopen`, { method: "PATCH" });
    }
    fetchIncidentsWrapper();
  }
  async function bulkResolveIncidents() {
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    const selectedIncidents = $incidents.filter(inc => inc.selectedForBulk && inc.status === "open");
    for (const inc of selectedIncidents) {
      await fetch(`http://localhost:8000/incidents/${inc.id}/resolve`, { method: "PATCH" });
    }
    fetchIncidentsWrapper();
  }
  async function bulkLinkMainAlerts(targetIncidentId) {
    if (!targetIncidentId) {
      console.warn("No target incident ID provided for bulk linking.");
      return;
    }
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    const selectedMainAlertIds = [];
    $incidents.forEach(inc => {
      if (inc.main_alerts && inc.main_alerts.length > 0) {
        inc.main_alerts.forEach(ma => {
          if (ma.selectedForBulk) {
            selectedMainAlertIds.push(ma.id);
          }
        });
      }
    });
    console.log("Selected main alert IDs for linking:", selectedMainAlertIds);
    if (selectedMainAlertIds.length === 0) {
      console.warn("No main alerts selected for bulk linking.");
      return;
    }
    const response = await fetch(`http://localhost:8000/incidents/${targetIncidentId}/bulk_link_main_alerts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ main_alert_ids: selectedMainAlertIds })
    });
    if (!response.ok) {
      console.error("Bulk linking failed:", response.statusText);
    }
    fetchIncidentsWrapper();
  }
  async function resolveIncident(incidentId) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/resolve`, { method: "PATCH" });
    recordAction({ type: "resolve", incidentId });
    fetchIncidentsWrapper();
  }
  async function definitivelyResolveIncident(incidentId) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/definitively_resolve`, { method: "PATCH" });
    fetchIncidentsWrapper();
  }
  async function reopenIncident(incidentId) {
    await fetch(`http://localhost:8000/incidents/${incidentId}/reopen`, { method: "PATCH" });
    recordAction({ type: "reopen", incidentId });
    fetchIncidentsWrapper();
  }
  async function renameIncident(incidentId, newName) {
    const inc = (await new Promise(resolve => {
      let $incidents;
      incidentsStore.subscribe(value => $incidents = value)();
      resolve($incidents.find(i => i.id === incidentId));
    }));
    if (!inc) return;
    const oldName = inc.incident_name;
    await fetch(`http://localhost:8000/incidents/${incidentId}/rename`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_name: newName })
    });
    recordAction({ type: "rename", incidentId, oldName, newName });
    fetchIncidentsWrapper();
  }
  function submitTitle(inc) {
    if (inc.renameText !== inc.incident_name) {
      renameIncident(inc.id, inc.renameText);
    }
    inc.editingTitle = false;
    fetchIncidentsWrapper();
  }
  async function updateSeverity(incidentId, newSeverity) {
    const inc = (await new Promise(resolve => {
      let $incidents;
      incidentsStore.subscribe(value => $incidents = value)();
      resolve($incidents.find(i => i.id === incidentId));
    }));
    if (!inc) return;
    const oldSeverity = inc.severity;
    inc.severity = newSeverity;
    try {
      console.log("Updating severity for incident", incidentId, "from", oldSeverity, "to", newSeverity);
      await fetch(`http://localhost:8000/incidents/${incidentId}/update_severity`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ severity: newSeverity })
      });
      recordAction({ type: "updateSeverity", incidentId, oldSeverity, newSeverity });
      fetchIncidentsWrapper();
    } catch (err) {
      console.error("Error updating severity:", err);
    }
  }
  async function updateTeam(incidentId, newTeam) {
    const inc = (await new Promise(resolve => {
      let $incidents;
      incidentsStore.subscribe(value => $incidents = value)();
      resolve($incidents.find(i => i.id === incidentId));
    }));
    if (!inc) return;
    const oldTeam = inc.team;
    inc.team = newTeam;
    try {
      console.log("Updating team for incident", incidentId, "from", oldTeam, "to", newTeam);
      await fetch(`http://localhost:8000/incidents/${incidentId}/update_team`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team: newTeam })
      });
      recordAction({ type: "updateTeam", incidentId, oldTeam, newTeam });
      fetchIncidentsWrapper();
    } catch (err) {
      console.error("Error updating team:", err);
    }
  }
  async function updateAssignee(incidentId, newAssignee) {
    const inc = (await new Promise(resolve => {
      let $incidents;
      incidentsStore.subscribe(value => $incidents = value)();
      resolve($incidents.find(i => i.id === incidentId));
    }));
    if (!inc) return;
    const oldAssignee = inc.assignee;
    inc.assignee = newAssignee;
    try {
      console.log("Updating assignee for incident", incidentId, "from", oldAssignee, "to", newAssignee);
      await fetch(`http://localhost:8000/incidents/${incidentId}/update_assignee`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assignee: newAssignee })
      });
      recordAction({ type: "updateAssignee", incidentId, oldAssignee, newAssignee });
      fetchIncidentsWrapper();
    } catch (err) {
      console.error("Error updating assignee:", err);
    }
  }

  async function updateStatus(incidentId, newStatus) {
    let $incidents;
    incidentsStore.subscribe(value => $incidents = value)();
    const inc = $incidents.find(i => i.id === incidentId);
    if (!inc) return;
    if (newStatus === inc.status) return;
    if (newStatus === "resolved" && inc.status === "open") {
      await fetch(`http://localhost:8000/incidents/${incidentId}/resolve`, { method: "PATCH" });
      recordAction({ type: "resolve", incidentId });
    } else if (newStatus === "open" && inc.status === "resolved") {
      await fetch(`http://localhost:8000/incidents/${incidentId}/reopen`, { method: "PATCH" });
      recordAction({ type: "reopen", incidentId });
    }
    fetchIncidentsWrapper();
  }

  async function linkMainAlert(incidentId, mainAlertId) {
    if (!mainAlertId) return;
    await fetch(`http://localhost:8000/incidents/${incidentId}/link/${mainAlertId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    fetchIncidentsWrapper();
  }
</script>

<svelte:head>
  <title>IIM - Incidents</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" crossorigin="anonymous" />
  <style>
    /* Existing styles remain unchanged */
    body { background-color: #f0f2f5; }
    body.dark-mode { background-color: #333; color: #eee; }
    body.dark-mode .incident-box { background-color: #444; border-color: #555; }
    body.dark-mode .main-alert-box { background-color: #555; border-color: #777; }
    body.dark-mode .comment-box { background-color: #555; border-color: #777; }
    body.dark-mode .form-control { background-color: #555; border-color: #777; color: #eee; }
    body.dark-mode .form-control::placeholder { color: #ccc; }
    body.dark-mode select.form-control { background-color: #555; border-color: #777; color: #eee; }
    body.dark-mode .dropdown-menu { background-color: #444; border-color: #666; color: #eee; }
    body.dark-mode .dropdown-item { background-color: #444; color: #eee; }
    body.dark-mode .dropdown-item:hover { background-color: #555; }
    .container-custom { max-width: 2000px; margin: 0 auto; }
    .incident-box {
      border: 1px solid #ddd;
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 1rem;
      background-color: #ffffff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .ma-fields {
  display: flex;
  flex-wrap: wrap;        /* So the fields can wrap on smaller screens */
  gap: 1rem;             /* A bit of spacing between fields */
}

.ma-fields span {
  margin-right: 1rem;    /* Optional: extra horizontal spacing */
}    
    .main-alert-box {
      background-color: #e9f7fe;
      border: 1px solid #007bff;
      border-radius: 0.5rem;
      padding: 0.5rem;
      margin-bottom: 0.5rem;
    }
    .comment-box {
      background-color: #e9f7ef;
      border: 1px solid #28a745;
      border-radius: 0.5rem;
      padding: 0.5rem;
      margin-bottom: 0.5rem;
    }
    .global-controls button { margin-right: 0.5rem; }
    .dropdown-text {
      background: none;
      border: none;
      padding: 0;
      margin: 0 2px;
      font-family: inherit;
      font-size: 12px;
      color: inherit;
      cursor: pointer;
    }
    .dropdown-menu {
      display: block;
      background: white;
      border: 1px solid #ccc;
      border-radius: 0.25rem;
      padding: 4px 0;
      position: absolute;
      z-index: 10;
      min-width: 200px;
    }
    .dropdown-item {
      background: none;
      border: none;
      width: 100%;
      text-align: left;
      padding: 4px 8px;
      cursor: pointer;
      font-family: inherit;
      font-size: inherit;
    }
    .dropdown-item:hover {
      background-color: #f1f1f1;
    }
    .title-text {
      cursor: pointer;
      font-size: 1rem;
      font-weight: bold;
    }
    .title-input {
  font-size: 1rem;
  font-weight: Italic;
  border: none;
  outline: none;
  background: rgba(230, 230, 230, 0.9);
  width: 100%;
}

    /* Force all text in compact rows to the same font settings */
    .compact-incident .compact-field,
    .compact-incident .dropdown-text,
    .compact-incident .dropdown-item,
    .compact-incident button {
      font-family: inherit !important;
      font-size: 1rem !important;
    }

    /* NEW: Compact view styling */
    .header-row {
      background-color: #f8f9fa;
      font-weight: bold;
      border-bottom: 2px solid #ddd;
    }
    .compact-incident {
      display: flex;
      align-items: center;
      padding: 0.02rem;
      border: 1px solid #ddd;
      border-radius: 0.5rem;
      margin-bottom: 0.1rem;
      background-color: #ffffff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      flex-wrap: nowrap;
    }
    .compact-field {
      padding: 0 .1rem;
      white-space: nowrap;
    }
    .compact-field.id {
      width: 3em;
      flex-shrink: 0;
      color: gray;
    }
    .compact-field.title {
      flex-grow: 1;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .compact-field.status {
      width: 5em;
      flex-shrink: 0;
    }
    .compact-field.first_alert {
    width: 90px;
    margin-right: 0.4rem;
    flex-shrink: 0;
    }
    .compact-field.last_alert {
      width: 90px;
      margin-right: 0.4rem;
      flex-shrink: 0;
}    
    .compact-field.severity {
      width: 100px;
      flex-shrink: 0;
    }
    .compact-field.team {
      width: 5em;
      flex-shrink: 0;
    }
    .compact-field.assignee {
      width: 120px;
      flex-shrink: 0;
    }
    /* New fields for incident in compact view */
    .compact-field.source {
      width: 5em;
      flex-shrink: 0;
    }
    .compact-field.host {
      width: 7em;
      flex-shrink: 0;
    }
    .compact-field.state {
      width: 80px;
      flex-shrink: 0;
    }
    .compact-field.alerts {
      width: 80px;
      flex-shrink: 0;
    }
    .compact-field.expand {
      width: 110px;
      margin-right: 0.4rem;
      flex-shrink: 0;
      text-align: center;
    }
  </style>
</svelte:head>

<div class="container container-custom">
  <!-- New Alert Section -->
  <div class="mb-4 comment-box">
    <form on:submit|preventDefault={createAlert}>
      <div class="form-group">
        <label for="alert-name">New Alert:</label>
        <input id="alert-name" class="form-control" bind:value={newAlertName} placeholder="Enter alert message" />
      </div>
      <button type="submit" class="btn btn-success">Create Alert</button>
    </form>
  </div>

  <!-- Global Controls -->
  <div class="global-controls mb-4">
    {#if $incidentsStore.length > 0}
      <button on:click={toggleCompactView} class="btn btn-secondary m-2">
        {compactView ? "Normal View" : "Compact View"}
      </button>
      <button on:click={toggleAllIncidents} class="btn btn-primary m-2">
        {allIncidentsCollapsed ? "Expand All Incidents" : "Collapse All Incidents"}
      </button>
      <button on:click={toggleAllMainAlerts} class="btn btn-info m-2">
        {allMainAlertsCollapsed ? "Expand All Main Alerts" : "Collapse All Main Alerts"}
      </button>
      <button on:click={toggleAllComments} class="btn btn-warning m-2">
        {allCommentsCollapsed ? "Expand All Comments" : "Collapse All Comments"}
      </button>


      {#if $incidentsStore.filter(inc => !inc.definitively_resolved).length > 0}
        {#if $incidentsStore.length > 0}
          <button on:click={toggleSelectAllIncidents} class="btn btn-secondary m-2">
            {$incidentsStore.every(item => item.selectedForBulk) ? 'Unselect All Incidents' : 'Select All Incidents'}
          </button>
        {/if}
      {/if}
      {#if $incidentsStore.filter(inc => inc.status === "resolved" && !inc.definitively_resolved).length > 0}
        {#if $filtersStore.statusFilter === "resolved" || $filtersStore.statusFilter === "all"}
          <button on:click={bulkReopenIncidents} class="btn btn-success m-2">
            Bulk Reopen Selected Incidents
          </button>
        {/if}
      {/if}
      {#if $incidentsStore.filter(inc => inc.status === "open").length > 0}
        {#if $filtersStore.statusFilter === "open" || $filtersStore.statusFilter === "all"}
          <button on:click={bulkResolveIncidents} class="btn btn-danger m-2">
            Bulk Resolve Selected Incidents
          </button>
        {/if}
      {/if}
    {/if}
    <!-- NEW: Column Settings Button -->
    {#if compactView}
    <div class="column-settings-container" style="display: inline-block; position: relative;">
      <button class="btn btn-outline-secondary m-2" on:click={() => showColumnSettings = !showColumnSettings}>
        Customize Columns
      </button>
      {#if showColumnSettings}
        <div class="dropdown-menu" style="left: auto; right: 0;">
          {#each Object.keys(columnVisibility) as colKey}
            <label class="dropdown-item">
              <input type="checkbox" bind:checked={columnVisibility[colKey]} />
              {colKey}
            </label>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
  </div>

  

  <!-- Bulk Link Section -->
  <div class="mb-4">
    {#if $incidentsStore.filter(inc => !inc.definitively_resolved).length < 0}
      <form on:submit|preventDefault={() => bulkLinkMainAlerts(bulkTargetIncidentId)}>
        <div class="form-row">
          <div class="form-group col-md-4">
            <input
              type="number"
              id="bulk-target"
              class="form-control"
              bind:value={bulkTargetIncidentId}
              placeholder="Enter target incident ID" />
          </div>
          <div class="form-group col-md-4 align-self-end">
            <button type="submit" class="btn btn-secondary">Bulk Link Selected Main Alerts</button>
          </div>
        </div>
      </form>
    {/if}
  </div>

  {#if compactView}
    <!-- Header row for compact view -->
    <div class="row">
      <article class="col-12 incident-box compact-incident header-row">
        {#if columnVisibility.id}
        <div class="compact-field id">ID</div>
        {/if}
        {#if columnVisibility.first_alert}
          <div class="compact-field first_alert">First</div>
        {/if}
        {#if columnVisibility.last_alert}
          <div class="compact-field last_alert">Last</div>
          {/if}
          {#if columnVisibility.host}
            <div class="compact-field host">Host</div>
          {/if}
        {#if columnVisibility.title}
          <div class="compact-field title">Title</div>
        {/if}
        {#if columnVisibility.status}
          <div class="compact-field status">Status</div>
        {/if}
        {#if columnVisibility.severity}
          <div class="compact-field severity">Severity</div>
        {/if}
        {#if columnVisibility.team}
          <div class="compact-field team">Team</div>
        {/if}
        {#if columnVisibility.assignee}
          <div class="compact-field assignee">Assignee</div>
        {/if}
        {#if columnVisibility.source}
          <div class="compact-field source">Source</div>
        {/if}
        {#if columnVisibility.state}
          <div class="compact-field state">State</div>
        {/if}
        {#if columnVisibility.alerts}
          <div class="compact-field alerts">Alerts</div>
        {/if}
        <div class="compact-field expand">Expand</div>
      </article>
    </div>
  {/if}

  <!-- Incident List -->
  <div class="row">
    {#each $incidentsStore as inc (inc.id)}
    {#if compactView && !inc.expandedOverride}
    <!-- Compact View Row -->
    <article
    class="col-12 incident-box compact-incident"
    draggable={inc.status !== "resolved" && !inc.definitively_resolved}
    on:dragstart={(e) => handleIncidentDragStart(e, inc)}
    on:drop={(e) => {
      e.preventDefault();
      const mainAlertData = e.dataTransfer.getData("application/main-alert");
      if (mainAlertData) {
        // If main alert data exists, transfer only that main alert
        handleMainAlertDrop(e, inc.id);
      } else {
        // Otherwise, transfer all main alerts from the dragged incident
        handleIncidentDrop(e, inc.id);
      }
    }}
    on:dragover={allowDrop}>
    {#if columnVisibility.id}
    <div class="compact-field id">#{inc.id}</div>
    {/if}
    {#if columnVisibility.first_alert}
    <div class="compact-field first_alert">{shortTimestamp(inc.first_alert_time)}</div>
    {/if}
    {#if columnVisibility.last_alert}
    <div class="compact-field last_alert">{shortTimestamp(inc.last_alert_time)}</div>
    {/if}
    {#if columnVisibility.host}
      <div class="compact-field host">{inc.host}</div>
    {/if}
          {#if columnVisibility.title}
            <div class="compact-field title" title={inc.incident_name}>
              {#if !inc.editingTitle}
                <span on:click={() => {
                  inc.editingTitle = true;
                  inc.renameText = inc.incident_name;
                }}>
                  {inc.incident_name}
                </span>
              {:else}
                <input
                  type="text"
                  class="title-input"
                  bind:value={inc.renameText}
                  on:blur={() => submitTitle(inc)}
                  on:keydown={(e) => { if(e.key === 'Enter') submitTitle(inc) }} />
              {/if}
            </div>
          {/if}
          {#if columnVisibility.status}
            <div class="compact-field status">
              {#if !inc.definitively_resolved}
              <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                <button type="button" class="dropdown-text" on:click={() => toggleDropdown(inc, "Status")}>
                  {inc.status}
                </button>
                {#if inc.showStatusDropdown}
                <div class="dropdown-menu" style="position: absolute; top: 100%; left: 0;">
                    <button
                      type="button"
                      class="dropdown-item"
                      on:click={() => { updateStatus(inc.id, "open"); inc.showStatusDropdown = false; }}>
                      open
                    </button>
                    <button
                      type="button"
                      class="dropdown-item"
                      on:click={() => { updateStatus(inc.id, "resolved"); inc.showStatusDropdown = false; }}>
                      resolved
                    </button>
                </div>
                {/if}
              </div>  
              {:else}
                <span>{inc.status}</span>
              {/if}
            </div>
          {/if}
          {#if columnVisibility.severity}
            <div class="compact-field severity">
              {#if !inc.definitively_resolved}
              <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                <button type="button" class="dropdown-text" on:click={() => toggleDropdown(inc, "Severity")}>
                  {inc.severity}
                </button>
                {#if inc.showSeverityDropdown}
                 <div class="dropdown-menu" style="position: absolute; top: 100%; left: 0;">
                    <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MAJOR"); inc.showSeverityDropdown = false; }}>MAJOR</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "HIGH"); inc.showSeverityDropdown = false; }}>HIGH</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MEDIUM"); inc.showSeverityDropdown = false; }}>MEDIUM</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "LOW"); inc.showSeverityDropdown = false; }}>LOW</button>
                  </div>
                {/if}
                </div>
              {:else}
                <span>{inc.severity}</span>
              {/if}
            </div>
          {/if}
          {#if columnVisibility.team}
            <div class="compact-field team">
              {#if !inc.definitively_resolved}
              <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                <button type="button" class="dropdown-text" on:click={() => toggleDropdown(inc, "Team")}>
                  {inc.team}
                </button>
                {#if inc.showTeamDropdown}
                 <div class="dropdown-menu" style="position: absolute; top: 100%; left: 0;">
                    <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team1"); inc.showTeamDropdown = false; }}>team1</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team2"); inc.showTeamDropdown = false; }}>team2</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team3"); inc.showTeamDropdown = false; }}>team3</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team_overkoepelend"); inc.showTeamDropdown = false; }}>team overkoepelend</button>
                  </div>
                {/if}
                </div>
              {:else}
                <span>{inc.team}</span>
              {/if}
            </div>
          {/if}
          {#if columnVisibility.assignee}
            <div class="compact-field assignee">
              {#if !inc.definitively_resolved}
              <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                <button type="button" class="dropdown-text" on:click={() => toggleDropdown(inc, "Assignee")}>
                  {inc.assignee}
                </button>
                {#if inc.showAssigneeDropdown}
                 <div class="dropdown-menu" style="position: absolute; top: 100%; left: 0;">
                    <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person1"); inc.showAssigneeDropdown = false; }}>person1</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person2"); inc.showAssigneeDropdown = false; }}>person2</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person3"); inc.showAssigneeDropdown = false; }}>person3</button>
                    <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person4"); inc.showAssigneeDropdown = false; }}>person4</button>
                  </div>
                {/if}
                </div>
              {:else}
                <span>{inc.assignee}</span>
              {/if}
            </div>
          {/if}
          {#if columnVisibility.source}
            <div class="compact-field source">{inc.source}</div>
          {/if}
          {#if columnVisibility.state}
            <div class="compact-field state">{inc.state}</div>
          {/if}
          {#if columnVisibility.alerts}
            <div class="compact-field alerts">{inc.alert_count}</div>
          {/if}
          <div class="compact-field expand">
            <button class="btn btn-sm btn-outline-primary" on:click={() => toggleRowExpansion(inc)}>
              {inc.expandedOverride ? "Collapse Row" : "Expand Row"}
            </button>
          </div>
        </article>
        {:else}
        <!-- Full View (Normal View) -->
        <article class="col-12 incident-box" 
        draggable={inc.status !== "resolved" && !inc.definitively_resolved}
        on:dragstart={(e) => handleIncidentDragStart(e, inc)}
        on:drop={(e) => {
          e.preventDefault();
          // Check if a main alert was dragged
          const mainAlertData = e.dataTransfer.getData("application/main-alert");
          if (mainAlertData) {
            handleMainAlertDrop(e, inc.id);
          } else {
            // Otherwise, transfer all main alerts from the incident
            handleIncidentDrop(e, inc.id);
          }
        }}
        on:dragover={allowDrop}>
          <header>
            <!-- Header Row: All fields except Title -->
            <div class="row align-items-center">
              <div class="col">
                <div class="d-flex flex-wrap align-items-center">
                  <div class="mr-3"><strong>#{inc.id}</strong></div>
                  {#if columnVisibility.first_alert}
                    <div class="mr-3"><small><strong>First:</strong> {shortTimestamp(inc.first_alert_time)}</small></div>
                  {/if}
                  {#if columnVisibility.last_alert}
                    <div class="mr-3"><small><strong>Last:</strong> {shortTimestamp(inc.last_alert_time)}</small></div>
                  {/if}
                  {#if columnVisibility.host}
                    <div class="mr-3"><small><strong>Host:</strong> {inc.host}</small></div>
                  {/if}
                  {#if columnVisibility.status}
                    <div class="mr-3" style="position: relative;">
                      <small><strong>Status:</strong></small>
                      {#if !inc.definitively_resolved}
                        <button type="button" class="dropdown-text ml-1"
                          on:click={() => toggleDropdown(inc, "Status")}
                          on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Status"))}
                          aria-haspopup="true" aria-expanded={inc.showStatusDropdown}>
                          {inc.status}
                        </button>
                        {#if inc.showStatusDropdown}
                          <div class="dropdown-menu" role="menu">
                            <button type="button" class="dropdown-item" on:click={() => { updateStatus(inc.id, "open"); inc.showStatusDropdown = false; }}>open</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateStatus(inc.id, "resolved"); inc.showStatusDropdown = false; }}>resolved</button>
                          </div>
                        {/if}
                      {:else}
                        <span>{inc.status}</span>
                      {/if}
                    </div>
                  {/if}
                  {#if columnVisibility.severity}
                    <div class="mr-3" style="position: relative;">
                      <small><strong>Severity:</strong></small>
                      {#if !inc.definitively_resolved}
                        <button type="button" class="dropdown-text ml-1"
                          on:click={() => toggleDropdown(inc, "Severity")}
                          on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Severity"))}
                          aria-haspopup="true" aria-expanded={inc.showSeverityDropdown}>
                          {inc.severity}
                        </button>
                        {#if inc.showSeverityDropdown}
                          <div class="dropdown-menu" role="menu">
                            <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MAJOR"); inc.showSeverityDropdown = false; }}>MAJOR</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "HIGH"); inc.showSeverityDropdown = false; }}>HIGH</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MEDIUM"); inc.showSeverityDropdown = false; }}>MEDIUM</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "LOW"); inc.showSeverityDropdown = false; }}>LOW</button>
                          </div>
                        {/if}
                      {:else}
                        <span>{inc.severity}</span>
                      {/if}
                    </div>
                  {/if}
                  {#if columnVisibility.team}
                    <div class="mr-3" style="position: relative;">
                      <small><strong>Team:</strong></small>
                      {#if !inc.definitively_resolved}
                      <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                        <button type="button" class="dropdown-text ml-1"
                          on:click={() => toggleDropdown(inc, "Team")}
                          on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Team"))}
                          aria-haspopup="true" aria-expanded={inc.showTeamDropdown}>
                          {inc.team}
                        </button>
                        {#if inc.showTeamDropdown}
                          <div class="dropdown-menu" role="menu">
                            <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team1"); inc.showTeamDropdown = false; }}>team1</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team2"); inc.showTeamDropdown = false; }}>team2</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team3"); inc.showTeamDropdown = false; }}>team3</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team_overkoepelend"); inc.showTeamDropdown = false; }}>team overkoepelend</button>
                          </div>
                        {/if}
                      </div>
                      {:else}
                        <span>{inc.team}</span>
                      {/if}
                    </div>
                  {/if}
                  {#if columnVisibility.assignee}
                    <div class="mr-3" style="position: relative;">
                      <small><strong>Assignee:</strong></small>
                      {#if !inc.definitively_resolved}
                      <div class="dropdown-wrapper" style="position: relative; display: inline-block;">
                        <button type="button" class="dropdown-text ml-1"
                          on:click={() => toggleDropdown(inc, "Assignee")}
                          on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Assignee"))}
                          aria-haspopup="true" aria-expanded={inc.showAssigneeDropdown}>
                          {inc.assignee}
                        </button>
                        {#if inc.showAssigneeDropdown}
                          <div class="dropdown-menu" role="menu">
                            <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person1"); inc.showAssigneeDropdown = false; }}>person1</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person2"); inc.showAssigneeDropdown = false; }}>person2</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person3"); inc.showAssigneeDropdown = false; }}>person3</button>
                            <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person4"); inc.showAssigneeDropdown = false; }}>person4</button>
                          </div>
                        {/if}
                      </div>
                      {:else}
                        <span>{inc.assignee}</span>
                      {/if}
                    </div>
                  {/if}
                  {#if columnVisibility.source}
                    <div class="mr-3"><small><strong>Source:</strong> {inc.source}</small></div>
                  {/if}
                  {#if columnVisibility.state}
                    <div class="mr-3"><small><strong>State:</strong> {inc.state}</small></div>
                  {/if}
                  {#if columnVisibility.alerts}
                    <div class="mr-3"><small><strong>Alerts:</strong> {inc.alert_count}</small></div>
                  {/if}
                </div>
              </div>
              <div class="col-auto">
                <div class="d-flex align-items-center">
                  {#if inc.status === "open"}
                    <button class="btn btn-sm btn-danger mr-2" on:click={() => resolveIncident(inc.id)}>Resolve</button>
                    <button class="btn btn-sm btn-dark mr-2" on:click={() => definitivelyResolveIncident(inc.id)}>Definitively Resolve</button>
                  {:else}
                    {#if !inc.definitively_resolved}
                      <button class="btn btn-sm btn-success mr-2" on:click={() => reopenIncident(inc.id)}>Reopen</button>
                    {/if}
                  {/if}
                  <button class="btn btn-sm btn-outline-secondary" on:click={() => toggleIncidentCollapse(inc)}>
                    {inc.collapsed ? "Expand More" : "Collapse"}
                  </button>
                  <!-- NEW: Always show the row expansion toggle button -->
                  <button class="btn btn-sm btn-outline-primary ml-2" on:click={() => toggleRowExpansion(inc)}>
                    {inc.expandedOverride ? "Collapse Row" : "Expand Row"}
                  </button>
                </div>
              </div>
            </div>
            <!-- Title Row: Title on its own row, editable when clicked -->
            <div class="row mt-1 mb-3 ml-4">
              <div class="col">
                {#if !inc.editingTitle}
                  <span class="title-text" on:click={() => { inc.editingTitle = true; inc.renameText = inc.incident_name; }}>
                    {inc.incident_name}
                  </span>
                {:else if !inc.definitively_resolved}
                  <input type="text" class="title-input" style="width:100%;" bind:value={inc.renameText} autofocus
                    on:blur={() => submitTitle(inc)}
                    on:keydown={(e) => { if (e.key === 'Enter') submitTitle(inc) }}/>
                {:else}
                  <span class="title-text">{inc.incident_name}</span>
                {/if}
              </div>
            </div>
            {#if !inc.collapsed}
              <!-- Expanded Section: Main Alerts & Comments -->
              <section class="incident-extra mt-2">
                {#if inc.showMainAlerts}
                  <div class="mt-2 p-2 border rounded main-alert-box" role="region" aria-label="Main Alerts">
                    <div class="d-flex justify-content-between align-items-center">
                      <h5 class="h6 m-1"></h5>
                      <button class="btn btn-sm btn-outline-primary" on:click={() => toggleMainAlerts(inc)}>Hide Main Alerts</button>
                    </div>
                    {#if inc.main_alerts && inc.main_alerts.length > 0}
                    <!-- Table container -->
                    <div class="table-responsive">
                      <table class="table table-bordered table-sm" style="margin-top: 0.5rem;">
                        <thead>
                          <tr>
                            <!-- One column for the checkbox -->
                            <th style="width: 2rem;"></th>
                            <th>Message</th>
                            <th>Counter</th>
                            <th>Last Alert</th>
                            <th>Source</th>
                            <th>Host</th>
                            <th>State</th>
                          </tr>
                        </thead>
                        <tbody>
                          {#each inc.main_alerts as ma}
                            <tr
                              draggable={inc.status !== "resolved" && !inc.definitively_resolved}
                              on:dragstart={(e) => handleMainAlertDragStart(e, ma, inc.id)}
                            >
                              <!-- If not definitively resolved, allow checkbox -->
                              <td>
                                {#if !inc.definitively_resolved}
                                  <input
                                    type="checkbox"
                                    bind:checked={ma.selectedForBulk}
                                    aria-label="Select main alert"
                                  />
                                {/if}
                              </td>
                              <td>{ma.message}</td>
                              <td>{ma.counter}</td>
                              <td>{ma.last_linked_time}</td>
                              <td>{ma.source}</td>
                              <td>{ma.host}</td>
                              <td>{ma.state}</td>
                            </tr>
                          {/each}
                        </tbody>
                      </table>
                    </div>
                  {:else}
                    <p class="mb-0">No main alerts available.</p>
                  {/if}
                  </div>
                {:else}
                  <button class="btn btn-sm btn-outline-primary mt-2" on:click={() => toggleMainAlerts(inc)}>Show Main Alerts</button>
                {/if}
                {#if inc.showComments}
                  <div class="mt-2 p-2 border rounded comment-box" role="region" aria-label="Comments">
                    <div class="d-flex justify-content-between align-items-center">
                      <h5 class="h6 m-0">Comments</h5>
                      <button type="button" class="btn btn-sm btn-outline-info" on:click={() => toggleComments(inc)}>Hide Comments</button>
                    </div>
                    {#if inc.comments && inc.comments.length > 0}
                      <ul class="list-unstyled mt-2">
                        {#each inc.comments as comment}
                          <li class="mb-3">
                            <div>
                              <small><strong>{formatTimestamp(comment.last_modified)}</strong></small>
                              <small class="ml-2"><strong>{comment.login_name}</strong></small>
                            </div>
                            <div class="mb-1">{@html comment.comment_text}</div>
                            <div class="d-flex">
                              {#if !inc.definitively_resolved}
                                <button class="btn btn-sm btn-outline-secondary mr-2" on:click={() => editComment(inc, comment)}>Modify</button>
                                <button class="btn btn-sm btn-outline-danger" on:click={() => deleteIncidentComment(inc.id, comment.id)}>Delete</button>
                              {/if}
                            </div>
                          </li>
                        {/each}
                      </ul>
                    {:else}
                      <p>No comments available.</p>
                    {/if}
                    {#if !inc.showCommentEditor && !inc.definitively_resolved}
                      <button class="btn btn-sm btn-outline-info mt-2" on:click={() => {
                        inc.showCommentEditor = true;
                        inc.editingComment = null;
                        inc.newCommentText = "";
                        inc.newCommentLogin = "";
                      }}>
                        Add New Comment
                      </button>
                    {/if}
                    {#if inc.showCommentEditor}
                      <form on:submit|preventDefault={() => submitComment(inc)} class="mt-3">
                        <QuillEditor bind:content={inc.newCommentText} />
                        <div class="form-row align-items-center mt-2">
                          <div class="col-md-4">
                            <label for="comment-login-{inc.id}" class="sr-only">Your Login Name</label>
                            <input type="text" id="comment-login-{inc.id}" class="form-control form-control-sm" placeholder="Your login name" bind:value={inc.newCommentLogin} />
                          </div>
                          <div class="col-auto">
                            <button type="submit" class="btn btn-sm btn-success">
                              {inc.editingComment ? "Update Comment" : "Add Comment"}
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-secondary ml-2" on:click={() => {
                              inc.showCommentEditor = false;
                              inc.editingComment = null;
                              inc.newCommentText = "";
                              inc.newCommentLogin = "";
                            }}>
                              Cancel
                            </button>
                          </div>
                        </div>
                      </form>
                    {/if}
                  </div>
                {:else}
                  <button class="btn btn-sm btn-outline-info mt-2" on:click={() => toggleComments(inc)}>Show Comments</button>
                {/if}
              </section>
            {/if}
          </header>
        </article>
      {/if}
    {/each}
  </div>
</div>
