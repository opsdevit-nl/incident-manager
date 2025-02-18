<script>
  import { onMount, setContext } from 'svelte';
  import { get } from 'svelte/store';
  import NavBar from '$lib/NavBar.svelte';
  import { filters } from '$lib/filters.js';
  import { fetchIncidents, loadPreferences, savePreferences } from '$lib/incidentHelpers.js';
  import { writable } from 'svelte/store';


  let allIncidentsCollapsed = true;
  let allMainAlertsCollapsed = true;
  let allCommentsCollapsed = true;

    // Subscribe to the filters store (we use get() to derive local variables)
  let statusFilter, teamFilter, assigneeFilter, severityFilter, sortBy, sortOrder, firstAlertStart, firstAlertEnd, lastAlertStart, lastAlertEnd;
  $: ({ statusFilter, teamFilter, assigneeFilter, severityFilter, sortBy, sortOrder, firstAlertStart, firstAlertEnd, lastAlertStart, lastAlertEnd } = get(filters));

  // Update the store when NavBar dispatches a change event.
  function handleStatusFilterChange(e) {
    filters.update(f => ({ ...f, statusFilter: e.detail }));
    console.log("Status changed to", e.detail);
  }
  function handleTeamFilterChange(e) {
    filters.update(f => ({ ...f, teamFilter: e.detail }));
  }
  function handleAssigneeFilterChange(e) {
    filters.update(f => ({ ...f, assigneeFilter: e.detail }));
  }
  function handleSeverityFilterChange(e) {
    filters.update(f => ({ ...f, severityFilter: e.detail }));
  }
  function handleSortByChange(e) {
    filters.update(f => ({ ...f, sortBy: e.detail }));
  }
  function handleSortOrderChange(e) {
    filters.update(f => ({ ...f, sortOrder: e.detail }));
  }
  // This handler listens for date filter changes.
  function handleDateFilterChange(e) {
    const { filterKey, value } = e.detail;
    console.log(`Layout: Date filter changed: ${filterKey} = ${value}`);
    filters.update(f => ({ ...f, [filterKey]: value }));
  }
  // Other variables/functions for the app.
  let userProfile = {
    fullName: "John Doe",
    role: "Admin",
    appVersion: "1.0.0"
  };

  let darkMode = false;
  let prefs = loadPreferences();

  // Create a Svelte store for incidents.
  const incidentsStore = writable([]);

  // (Undo/redo functions and other helper functions remain as needed.)
  let undoStack = [];
  let redoStack = [];

  function recordAction(action) {
    if (action.incidentId !== undefined) {
      undoStack.push(action);
      console.log("Action recorded:", action);
      redoStack = [];
    }
  }

  async function fetchIncidentsWrapper() {
    const f = get(filters);
    const data = await fetchIncidents(
      f.statusFilter,
      f.teamFilter,
      f.assigneeFilter,
      f.severityFilter,
      true,  // For example, using true for collapse states
      true,
      true,
      prefs,
      f.firstAlertStart,
      f.firstAlertEnd,
      f.lastAlertStart,
      f.lastAlertEnd,             
      // allIncidentsCollapsed,
      // allMainAlertsCollapsed,
      // allCommentsCollapsed,
      // prefs
    );
    // Apply client-side sorting
    incidentsStore.set([...data]);
    console.log("Fetched and sorted incidents:", data);
  }

  async function undoAction() {
    if (!undoStack.length) {
      console.log("Undo stack is empty");
      return;
    }
    const action = undoStack.pop();
    console.log("Undo action:", action);
    try {
      switch (action.type) {
        case "create":
          if (action.alertId && action.incidentId) {
            await fetch(`http://localhost:8000/alerts/${action.alertId}`, { method: "DELETE" });
            await fetch(`http://localhost:8000/incidents/${action.incidentId}`, { method: "DELETE" });
          }
          break;
        case "rename":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/rename`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_name: action.oldName })
          });
          break;
        case "updateSeverity":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_severity`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ severity: action.oldSeverity })
          });
          break;
        case "updateTeam":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_team`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ team: action.oldTeam })
          });
          break;
        case "updateAssignee":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_assignee`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ assignee: action.oldAssignee })
          });
          break;
        case "resolve":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/reopen`, { method: "PATCH" });
          break;
        case "reopen":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/resolve`, { method: "PATCH" });
          break;
        default:
          console.warn("Undo not implemented for action type:", action.type);
      }
      redoStack.push(action);
      // Wait 500ms for backend to update, then refresh the store.
      await new Promise(resolve => setTimeout(resolve, 500));
      await fetchIncidentsWrapper();
    } catch (err) {
      console.error("Undo error:", err);
    }
    console.log("Undo action executed");
  }

  async function redoAction() {
    if (!redoStack.length) {
      console.log("Redo stack is empty");
      return;
    }
    const action = redoStack.pop();
    console.log("Redo action:", action);
    try {
      switch (action.type) {
        case "create":
          const response = await fetch("http://localhost:8000/alerts/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ alert_name: action.alertName })
          });
          const data = await response.json();
          action.alertId = data.alert.id;
          action.incidentId = data.incident?.id || data.incident?.incident_id;
          break;
        case "rename":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/rename`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_name: action.newName })
          });
          break;
        case "updateSeverity":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_severity`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ severity: action.newSeverity })
          });
          break;
        case "updateTeam":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_team`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ team: action.newTeam })
          });
          break;
        case "updateAssignee":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/update_assignee`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ assignee: action.newAssignee })
          });
          break;
        case "resolve":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/resolve`, { method: "PATCH" });
          break;
        case "reopen":
          await fetch(`http://localhost:8000/incidents/${action.incidentId}/reopen`, { method: "PATCH" });
          break;
        default:
          console.warn("Redo not implemented for action type:", action.type);
      }
      undoStack.push(action);
      // Wait 500ms for backend to update, then refresh the store.
      await new Promise(resolve => setTimeout(resolve, 500));
      await fetchIncidentsWrapper();
    } catch (err) {
      console.error("Redo error:", err);
    }
    console.log("Redo action executed");
  }

  function toggleDropdown(inc, field) {
    inc["show" + field + "Dropdown"] = !inc["show" + field + "Dropdown"];
    // Update the shared store so the UI reflects the change
    incidentsStore.update(items =>
      items.map(item =>
        item.id === inc.id ? { ...item, ["show" + field + "Dropdown"]: inc["show" + field + "Dropdown"] } : item
      )
    );
    fetchIncidentsWrapper();
  }

  function toggleDarkMode() {
    darkMode = !darkMode;
    prefs.darkMode = darkMode;
    savePreferences(prefs);
    if (darkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  }

  function logout() {
    window.location.href = '/logout';
  }

  onMount(() => {
    prefs = loadPreferences();
    darkMode = prefs.darkMode;
    if (darkMode) {
      document.body.classList.add("dark-mode");
    }
    allIncidentsCollapsed = prefs.allCollapsed;
    allCommentsCollapsed = prefs.allCommentsCollapsed !== undefined ? prefs.allCommentsCollapsed : true;
    allMainAlertsCollapsed = prefs.allMainAlertsCollapsed !== undefined ? prefs.allMainAlertsCollapsed : true;
    window.addEventListener("keydown", (e) => {
      console.log("Key pressed:", e.key);
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === "z") {
        e.preventDefault();
        console.log("Keyboard shortcut: Undo detected");
        undoAction();
      } else if ((e.ctrlKey || e.metaKey) && (e.key === "y" || (e.shiftKey && e.key === "z"))) {
        e.preventDefault();
        console.log("Keyboard shortcut: Redo detected");
        redoAction();
      }
    });
    fetchIncidentsWrapper();
  });

    // Provide contexts to child pages.
  setContext("filters", filters);
  setContext("undoManager", { recordAction, undoAction, redoAction });
  setContext("incidentsStore", incidentsStore);
</script>

<NavBar
  {userProfile}
  {darkMode}
  {undoAction}
  {redoAction}
  {toggleDarkMode}
  {logout}
  {statusFilter}
  {teamFilter}
  {assigneeFilter}
  {severityFilter}
  {sortBy}
  {sortOrder}
  on:statusFilterChange={handleStatusFilterChange}
  on:teamFilterChange={handleTeamFilterChange}
  on:assigneeFilterChange={handleAssigneeFilterChange}
  on:severityFilterChange={handleSeverityFilterChange}
  on:sortByChange={handleSortByChange}
  on:sortOrderChange={handleSortOrderChange}
  on:dateFilterChange={handleDateFilterChange}
/>


<slot />
