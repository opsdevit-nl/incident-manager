<script>
  import QuillEditor from "$lib/QuillEditor.svelte";
  import { onMount, getContext } from "svelte"; 
  import { filters } from '$lib/filters.js';
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
  let statusFilter = "open";
  let teamFilter = "";
  let assigneeFilter = "";
  let severityFilter = "";
  let linkMainAlertId = "";
  let bulkTargetIncidentId = "";

  // Global collapse states – default values
  let allIncidentsCollapsed = true;
  let allMainAlertsCollapsed = true;
  let allCommentsCollapsed = true;

  // New date filter variables for first_alert_time and last_alert_time.
  let firstAlertStart = "";
  let firstAlertEnd = "";
  let lastAlertStart = "";
  let lastAlertEnd = "";

  // const filtersStore = getContext("filters");
  // // let $filters;
  // filtersStore.subscribe(value => $filters = value);
  
  // Load saved preferences from your helper
  let prefs = loadPreferences();
  // Ensure the object for comment collapse is present.
  if (!prefs.commentsCollapsed) {
    prefs.commentsCollapsed = {};
  }


 // At the bottom of your script block, add:
  let socket;
  onMount(() => {
    if (browser) {
      // // Read filter preferences from localStorage
      // statusFilter = localStorage.getItem("statusFilter") || "open";
      // teamFilter = localStorage.getItem("teamFilter") || "";
      // assigneeFilter = localStorage.getItem("assigneeFilter") || "";
      // severityFilter = localStorage.getItem("severityFilter") || "";

      // Read collapse preferences; default to true if not explicitly set to "false"
      allIncidentsCollapsed = localStorage.getItem("allIncidentsCollapsed") !== "false";
      allMainAlertsCollapsed = localStorage.getItem("allMainAlertsCollapsed") !== "false";
      allCommentsCollapsed = localStorage.getItem("allCommentsCollapsed") !== "false";
    }
    // Use a zero-delay timeout to ensure the above reads finish before fetching.
    setTimeout(() => {
      fetchIncidentsWrapper();
    }, 0);

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
    // Dependency: $filtersStore; when it changes, re-run fetchIncidentsWrapper()
    $filtersStore;
    fetchIncidentsWrapper();
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
    // Convert local time to UTC by adding the timezone offset in milliseconds
    startDate = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000);
    console.log("First Alert Start selected:", f.firstAlertStart, "converted to UTC:", startDate.toISOString());
    data = data.filter(inc => {
      // Append "Z" to ensure the incident date is interpreted as UTC
      let incidentDate = new Date(inc.first_alert_time + "Z");
      console.log("Comparing incident first_alert_time:", incidentDate.toISOString(), ">= filter:", startDate.toISOString());
      return incidentDate >= startDate;
    });
  }
  if (f.firstAlertEnd && !isNaN(new Date(f.firstAlertEnd).getTime())) {
    let endDate = new Date(f.firstAlertEnd);
    endDate = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000);
    console.log("First Alert End selected:", f.firstAlertEnd, "converted to UTC:", endDate.toISOString());
    data = data.filter(inc => {
      let incidentDate = new Date(inc.first_alert_time + "Z");
      return incidentDate <= endDate;
    });
  }

  // --- Date/time filtering for last_alert_time ---
  if (f.lastAlertStart && !isNaN(new Date(f.lastAlertStart).getTime())) {
    let startDate = new Date(f.lastAlertStart);
    startDate = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000);
    console.log("Last Alert Start selected:", f.lastAlertStart, "converted to UTC:", startDate.toISOString());
    data = data.filter(inc => {
      if (!inc.last_alert_time) return false;
      let incidentDate = new Date(inc.last_alert_time + "Z");
      return incidentDate >= startDate;
    });
  }
  if (f.lastAlertEnd && !isNaN(new Date(f.lastAlertEnd).getTime())) {
    let endDate = new Date(f.lastAlertEnd);
    endDate = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000);
    console.log("Last Alert End selected:", f.lastAlertEnd, "converted to UTC:", endDate.toISOString());
    data = data.filter(inc => {
      if (!inc.last_alert_time) return false;
      let incidentDate = new Date(inc.last_alert_time + "Z");
      return incidentDate <= endDate;
    });
  }


    // Apply client-side sorting.
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

  // --------------------------
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
    // In fetchIncidents() we compute showMainAlerts as:
    //   (prefs.mainAlertsCollapsed[inc.id] !== undefined) ? !prefs.mainAlertsCollapsed[inc.id] : !allMainAlertsCollapsed;
    // So store the inverse of newVal.
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
    // Similarly, store the inverse in prefs.commentsCollapsed.
    saveCommentsPreference(inc.id, !newVal);
  }

  // For dropdowns, ensure that opening one closes the others.
  const dropdownFields = ["Status", "Severity", "Team", "Assignee"];
  function toggleDropdown(inc, field) {
    // Close all dropdowns except the one for the selected field.
    dropdownFields.forEach(f => {
      if (f !== field) {
        inc["show" + f + "Dropdown"] = false;
      }
    });
    // Toggle the selected dropdown.
    inc["show" + field + "Dropdown"] = !inc["show" + field + "Dropdown"];

    // Update the store so that the UI reflects these changes.
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
  // If expanding main alerts, force incidents to expand:
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
    // Save the main alerts collapse preference for each incident
    prefs.mainAlertsCollapsed[item.id] = allMainAlertsCollapsed;
    // Also force incident expansion if main alerts are expanded
    if (!allMainAlertsCollapsed) {
      prefs.collapsed[item.id] = false;
    }
  });
  savePreferences(prefs);
  fetchIncidentsWrapper();
}

function toggleAllComments() {
  allCommentsCollapsed = !allCommentsCollapsed;
  // If expanding comments, force incidents to expand:
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
    // Save the comments collapse preference for each incident
    prefs.commentsCollapsed[item.id] = allCommentsCollapsed;
    // Also force incident expansion if comments are expanded
    if (!allCommentsCollapsed) {
      prefs.collapsed[item.id] = false;
    }
  });
  savePreferences(prefs);
  fetchIncidentsWrapper();
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

  // -------------------------------
  // Other helper functions

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
      body: JSON.stringify({ alert_name: newAlertName })
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
    // Note: You may need to adjust this if you want to update the shared store.
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

  // UPDATED: Bulk linking now sends a single POST to the bulk endpoint.
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

  // NEW: Function to update the status of an incident.
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



  // // Update localStorage when filters change
  // function onStatusChange() {
  //   if (browser) localStorage.setItem("statusFilter", statusFilter);
  //   fetchIncidentsWrapper();
  // }
  // function onTeamChange() {
  //   if (browser) localStorage.setItem("teamFilter", teamFilter);
  //   fetchIncidentsWrapper();
  // }
  // function onAssigneeChange() {
  //   if (browser) localStorage.setItem("assigneeFilter", assigneeFilter);
  //   fetchIncidentsWrapper();
  // }
  // function onSeverityChange() {
  //   if (browser) localStorage.setItem("severityFilter", severityFilter);
  //   fetchIncidentsWrapper();
  // }
</script>

<svelte:head>
  <title>IIM - Incidents</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" crossorigin="anonymous" />
  <style>
    /* Your styles remain unchanged */
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
    .container-custom { max-width: 1500px; margin: 0 auto; }
    .incident-box { border: 1px solid #ddd; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .main-alert-box { background-color: #e9f7fe; border: 1px solid #007bff; border-radius: 0.5rem; padding: 0.5rem; margin-bottom: 0.5rem; }
    .comment-box { background-color: #e9f7ef; border: 1px solid #28a745; border-radius: 0.5rem; padding: 0.5rem; margin-bottom: 0.5rem; }
    .global-controls button { margin-right: 0.5rem; }
    .dropdown-text { background: none; border: none; padding: 0; margin: 0 2px; font-family: inherit; font-size: 12px; color: inherit; cursor: pointer; }
    .dropdown-menu { display: block; background: white; border: 1px solid #ccc; border-radius: 0.25rem; padding: 4px 0; position: absolute; z-index: 10; min-width: 200px; }
    .dropdown-item { background: none; border: none; width: 100%; text-align: left; padding: 4px 8px; cursor: pointer; font-family: inherit; font-size: inherit; }
    .dropdown-item:hover { background-color: #f1f1f1; }
    .title-text { cursor: pointer; font-size: 1rem; font-weight: bold; }
    .title-input { font-size: 1rem; font-weight: bold; border: none; outline: none; background: rgba(255,255,255,0.9); }
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


  <div class="global-controls mb-4">
    {#if $incidentsStore.length > 0}
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
  </div>

  <!-- Bulk Link Section -->
  <div class="mb-4">
    {#if $incidentsStore.filter(inc => !inc.definitively_resolved).length < 0}
    <form on:submit|preventDefault={() => bulkLinkMainAlerts(bulkTargetIncidentId)}>
      <div class="form-row">
        <div class="form-group col-md-4">
          <input type="number" id="bulk-target" class="form-control" bind:value={bulkTargetIncidentId} placeholder="Enter target incident ID" />
        </div>
        <div class="form-group col-md-4 align-self-end">
          <button type="submit" class="btn btn-secondary">Bulk Link Selected Main Alerts</button>
        </div>
      </div>
    </form>
    {/if}
  </div>

  <!-- Incident List -->
  <div class="row">
    {#each $incidentsStore as inc (inc.id)}
      <article class="col-12 incident-box" draggable={inc.status !== "resolved" && !inc.definitively_resolved }
        on:dragstart={(e) => handleIncidentDragStart(e, inc)}
        on:drop={(e) => handleIncidentDrop(e, inc.id)}
        on:dragover={allowDrop}>
        <!-- Incident Header -->
        <header>
          <div class="row align-items-center">
            <div class="col">
              <div class="d-flex flex-wrap align-items-center">
                <!-- Checkbox, ID -->
                <div class="mr-3">
                  {#if !inc.definitively_resolved}
                  <input type="checkbox" bind:checked={inc.selectedForBulk} aria-label="Select incident for bulk actions" />
                  {/if}
                </div>
                <div class="mr-3"><strong>#{inc.id}</strong></div>
                <!-- Status Dropdown -->
                {#if inc.definitively_resolved}
                  <div class="mr-3">
                    <small><strong>Status:</strong> def-resolved</small>
                  </div>
                {:else}
                  <div class="mr-3" style="position: relative;">
                    <small><strong>Status:</strong></small>
                    <button type="button" class="dropdown-text ml-1"
                      on:click={() => toggleDropdown(inc, "Status")}
                      on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Status"))}
                      aria-haspopup="true" aria-expanded={inc.showStatusDropdown}>
                      {inc.status}
                    </button>
                    {#if inc.showStatusDropdown}
                      <div class="dropdown-menu" role="menu">
                        <button type="button" class="dropdown-item"
                          on:click={() => { updateStatus(inc.id, "open"); inc.showStatusDropdown = false; }}>
                          open
                        </button>
                        <button type="button" class="dropdown-item"
                          on:click={() => { updateStatus(inc.id, "resolved"); inc.showStatusDropdown = false; }}>
                          resolved
                        </button>
                      </div>
                    {/if}
                  </div>
                {/if}
                <!-- Severity Dropdown -->
                <div class="mr-3" style="position: relative;">
                  <small><strong>Severity:</strong></small>
                  {#if !inc.definitively_resolved}
                  <button type="button" class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Severity")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Severity"))}
                    aria-haspopup="true" aria-expanded={inc.showSeverityDropdown}>
                    {inc.severity}
                  </button>
                  {:else}
                  <button type="button" class="dropdown-text ml-1">{inc.severity}</button>
                  {/if}
                  {#if inc.showSeverityDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MAJOR"); inc.showSeverityDropdown = false; }}>
                        MAJOR
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "HIGH"); inc.showSeverityDropdown = false; }}>
                        HIGH
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "MEDIUM"); inc.showSeverityDropdown = false; }}>
                        MEDIUM
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateSeverity(inc.id, "LOW"); inc.showSeverityDropdown = false; }}>
                        LOW
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3" style="position: relative;">
                  <small><strong>Team:</strong></small>
                  {#if !inc.definitively_resolved}
                  <button type="button" class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Team")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Team"))}
                    aria-haspopup="true" aria-expanded={inc.showTeamDropdown}>
                    {inc.team}
                  </button>
                  {:else}
                  <button type="button" class="dropdown-text ml-1">{inc.team}</button>
                  {/if}
                  {#if inc.showTeamDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team1"); inc.showTeamDropdown = false; }}>
                        team1
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team2"); inc.showTeamDropdown = false; }}>
                        team2
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team3"); inc.showTeamDropdown = false; }}>
                        team3
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateTeam(inc.id, "team_overkoepelend"); inc.showTeamDropdown = false; }}>
                        team overkoepelend
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3" style="position: relative;">
                  <small><strong>Assignee:</strong></small>
                  {#if !inc.definitively_resolved}
                  <button type="button" class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Assignee")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Assignee"))}
                    aria-haspopup="true" aria-expanded={inc.showAssigneeDropdown}>
                    {inc.assignee}
                  </button>
                  {:else}
                  <button type="button" class="dropdown-text ml-1">{inc.assignee}</button>
                  {/if}
                  {#if inc.showAssigneeDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person1"); inc.showAssigneeDropdown = false; }}>
                        person1
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person2"); inc.showAssigneeDropdown = false; }}>
                        person2
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person3"); inc.showAssigneeDropdown = false; }}>
                        person3
                      </button>
                      <button type="button" class="dropdown-item" on:click={() => { updateAssignee(inc.id, "person4"); inc.showAssigneeDropdown = false; }}>
                        person4
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3"><small><strong>Alerts:</strong> {inc.alert_count}</small></div>
                <div class="mr-3"><small><strong>Reopens:</strong> {inc.reopen_count}</small></div>
                <div class="mr-3"><small><strong>Wiki:</strong> {inc.wiki_url}</small></div>
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
                  {inc.collapsed ? "Expand" : "Collapse"}
                </button>
              </div>
            </div>
          </div>
          <!-- Title Row -->
          <div class="row mt-1 mb-3 ml-4">
            <div class="col">
              {#if !inc.editingTitle}

                <span class="title-text" on:click={() => {inc.editingTitle = true; inc.renameText = inc.incident_name; }}>
                  {inc.incident_name}
                </span>
              {:else if !inc.definitively_resolved}
                <input type="text" class="title-input" bind:value={inc.renameText} autofocus on:blur={() => submitTitle(inc)} on:keydown={(e) => { if (e.key === 'Enter') { submitTitle(inc) } }} />
              {:else}
                <span class="title-text">{inc.incident_name}</span>
              {/if}
              <br />
            </div>
          </div>
          <!-- Expanded View: Main Alerts & Comments -->
          {#if !inc.collapsed}
            <section class="incident-extra">
              {#if inc.showMainAlerts}
                <div on:drop={(e) => handleMainAlertDrop(e, inc.id)} on:dragover={allowDrop}>
                  <div class="mt-2 p-2 border rounded main-alert-box" role="region" aria-label="Main Alerts">
                    <div class="d-flex justify-content-between align-items-center">
                      <h5 class="h6 m-1">Main Alerts</h5>
                      <button class="btn btn-sm btn-outline-primary" on:click={() => toggleMainAlerts(inc)}>
                        Hide Main Alerts
                      </button>
                    </div>
                    {#if inc.main_alerts && inc.main_alerts.length > 0}
                      <ul class="list-unstyled mb-0 mt-2">
                        {#each inc.main_alerts as ma}
                          <li class="mb-1 d-flex align-items-center" draggable={inc.status !== "resolved" && !inc.definitively_resolved }
                              on:dragstart={(e) => handleMainAlertDragStart(e, ma, inc.id)}>
                            {#if !inc.definitively_resolved}
                            <input type="checkbox" bind:checked={ma.selectedForBulk} aria-label="Select main alert" class="mr-2" />
                            {/if}
                            <span>
                              <strong>ID:</strong> {ma.id} | <strong>Message:</strong> {ma.message} | <strong>Counter:</strong> {ma.counter} | <strong>Last Alert:</strong> {ma.last_linked_time}
                            </span>
                          </li>
                        {/each}
                      </ul>
                    {:else}
                      <p class="mb-0 mt-2">No main alerts available.</p>
                    {/if}
                  </div>
                </div>
              {:else}
                <button class="btn btn-sm btn-outline-primary" on:click={() => toggleMainAlerts(inc)}>
                  Show Main Alerts
                </button>
              {/if}
              <div class="mb-3">
                {#if inc.showComments}
                  <div class="mt-2 p-2 border rounded comment-box" role="region" aria-label="Comments">
                    <div class="d-flex justify-content-between align-items-center">
                      <h5 class="h6 m-0">Comments</h5>
                      <button type="button" class="btn btn-sm btn-outline-info" on:click={() => toggleComments(inc)}>
                        Hide Comments
                      </button>
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
                              <button type="button" class="btn btn-sm btn-outline-secondary mr-2" on:click={() => editComment(inc, comment)}>
                                Modify
                              </button>
                              <button type="button" class="btn btn-sm btn-outline-danger" on:click={() => deleteIncidentComment(inc.id, comment.id)}>
                                Delete
                              </button>
                              {/if}
                            </div>
                          </li>
                        {/each}
                      </ul>
                    {:else}
                      <p class="mt-2">No comments available.</p>
                    {/if}
                    {#if !inc.showCommentEditor}
                    {#if !inc.definitively_resolved}
                      <div class="mt-3">
                        <button type="button" class="btn btn-sm btn-outline-info" on:click={() => {
                          inc.showCommentEditor = true;
                          inc.editingComment = null;
                          inc.newCommentText = "";
                          inc.newCommentLogin = "";
                        }}>
                          Add New Comment
                        </button>
                      </div>
                      {/if}
                    {/if}
                    {#if inc.showCommentEditor}
                      <div class="mt-3">
                        <form on:submit|preventDefault={() => submitComment(inc)}>
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
                      </div>
                    {/if}
                  </div>
                {:else}
                  <button type="button" class="btn btn-sm btn-outline-info mt-2" on:click={() => toggleComments(inc)}>
                    Show Comments
                  </button>
                {/if}
              </div>
            </section>
          {/if}
      </article>
    {/each}
  </div>
</div>
