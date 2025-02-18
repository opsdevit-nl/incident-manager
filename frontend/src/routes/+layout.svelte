<script>
  import { onMount, setContext } from 'svelte';
  import { writable } from 'svelte/store';
  import NavBar from '$lib/NavBar.svelte';
  import { fetchIncidents, loadPreferences, savePreferences } from '$lib/incidentHelpers.js';

  let allIncidentsCollapsed = true;
  let allMainAlertsCollapsed = true;
  let allCommentsCollapsed = true;

  let statusFilter = "open";
  let teamFilter = "";
  let assigneeFilter = "";
  let severityFilter = "";
  let linkMainAlertId = "";
  let bulkTargetIncidentId = "";

  let userProfile = {
    fullName: "John Doe",
    role: "Admin",
    appVersion: "1.0.0"
  };

  let darkMode = false;
  let prefs = loadPreferences();

  // Create a Svelte store for incidents.
  const incidentsStore = writable([]);

  // Shared undo/redo stacks and functions
  let undoStack = [];
  let redoStack = [];

  function recordAction(action) {
    if (action.incidentId !== undefined) {
      undoStack.push(action);
      console.log("Action recorded:", action, "UndoStack:", undoStack);
      redoStack = [];
    }
  }

  async function fetchIncidentsWrapper() {
    const data = await fetchIncidents(
      statusFilter,
      teamFilter,
      assigneeFilter,
      severityFilter,
      allIncidentsCollapsed,
      allMainAlertsCollapsed,
      allCommentsCollapsed,
      prefs
    );
    // Force a new array reference so the store updates.
    incidentsStore.set([...data]);
    console.log("Fetched incidents:", data);
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

  // Provide the shared undo manager and incidents store to child pages.
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
/>

<slot />
