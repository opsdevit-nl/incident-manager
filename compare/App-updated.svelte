<script>
  import QuillEditor from "./QuillEditor.svelte";
  import { onMount } from "svelte";

  // Dummy user profile – replace with real data as needed.
  let userProfile = {
    fullName: "John Doe",
    role: "Admin", // or "User"
    appVersion: "1.0.0"
  };

  // State for user profile menu dropdown.
  let showUserMenu = false;

  // Dark mode preference
  let darkMode = false;

  // State for notifications toggle
  let notificationsOn = true;

  // Logout function
  function logout() {
    // Perform logout actions here
    window.location.href = "/logout";
  }

  // Toggle notifications
  function toggleNotifications() {
    notificationsOn = !notificationsOn;
  }

  // Toggle dark mode
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

  // Data and filter variables
  let incidents = [];
  let newAlertName = "";
  let statusFilter = "open";
  let teamFilter = "";
  let assigneeFilter = "";
  let severityFilter = "";
  let linkMainAlertId = "";
  let bulkTargetIncidentId = "";
  let allMainAlertsCollapsed = true;  // global default for main alerts collapsed
  let allCommentsCollapsed = true;    // collapse comments by default
  let allIncidentsCollapsed = true;   // default: all incidents collapsed

  // Preferences stored in localStorage
  const PREF_KEY = "incidentPreferences";
  let prefs = loadPreferences();

  function loadPreferences() {
    const pref = localStorage.getItem(PREF_KEY);
    if (pref) {
      let p = JSON.parse(pref);
      if (p.darkMode === undefined) p.darkMode = false;
      return p;
    }
    // Default preferences for incidents, comments, main alerts, and dark mode.
    return {
      allCollapsed: true,
      collapsed: {},
      allCommentsCollapsed: true,
      allMainAlertsCollapsed: true,
      mainAlertsCollapsed: {},
      darkMode: false
    };
  }

  function savePreferences(p) {
    localStorage.setItem(PREF_KEY, JSON.stringify(p));
  }

  function handleKeyAction(e, actionFn) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      actionFn();
    }
  }

  // Undo/redo stacks
  let undoStack = [];
  let redoStack = [];

  function recordAction(action) {
    if (action.incidentId !== undefined) {
      undoStack.push(action);
      redoStack = [];
    }
  }

  async function undoAction() {
    // ...
    // existing undo logic
  }

  async function redoAction() {
    // ...
    // existing redo logic
  }

  function formatTimestamp(ts) {
    // ...
  }

  async function fetchIncidents() {
    // ...
  }

  onMount(() => {
    prefs = loadPreferences();
    allIncidentsCollapsed = prefs.allCollapsed;
    allCommentsCollapsed = prefs.allCommentsCollapsed !== undefined ? prefs.allCommentsCollapsed : true;
    allMainAlertsCollapsed = prefs.allMainAlertsCollapsed !== undefined ? prefs.allMainAlertsCollapsed : true;
    darkMode = prefs.darkMode;
    if (darkMode) {
      document.body.classList.add("dark-mode");
    }
    fetchIncidents();
  });

  function toggleAllIncidents() {
    // ...
  }

  function toggleAllMainAlerts() {
    // ...
  }

  function toggleAllComments() {
    // ...
  }

  function selectAllIncidents() {
    // ...
  }

  function toggleIncidentCollapse(inc) {
    // ...
  }

  function toggleMainAlerts(inc) {
    // ...
  }

  function toggleComments(inc) {
    // ...
  }

  // Drag & drop handlers
  function handleDragStart(event, mainAlert, fromIncidentId) {
    // ...
  }

  function handleIncidentDragStart(event, incident) {
    // ...
  }

  function handleIncidentDrop(event, targetIncidentId) {
    // ...
  }

  function allowDrop(event) {
    // ...
  }

  // Filter change
  function onStatusChange() {
    // ...
  }
  function onTeamChange() {
    // ...
  }
  function onAssigneeChange() {
    // ...
  }
  function onSeverityChange() {
    // ...
  }

  // Comment-related
  async function addIncidentComment(incidentId, loginName, commentText) {
    // ...
  }
  async function updateIncidentComment(incidentId, commentId, commentText) {
    // ...
  }
  async function submitComment(inc) {
    // ...
  }
  function editComment(inc, comment) {
    // ...
  }
  async function deleteIncidentComment(incidentId, commentId) {
    // ...
  }

  // Alert creation
  async function createAlert() {
    // ...
  }

  // Bulk actions
  async function bulkReopenIncidents() {
    // ...
  }
  async function bulkResolveIncidents() {
    // ...
  }
  async function bulkLinkMainAlerts(targetIncidentId) {
    // ...
  }

  // Incident resolution
  async function resolveIncident(incidentId) {
    // ...
  }
  async function definitivelyResolveIncident(incidentId) {
    // ...
  }
  async function reopenIncident(incidentId) {
    // ...
  }

  // Rename incident
  async function renameIncident(incidentId, newName) {
    // ...
  }
  function submitTitle(inc) {
    // ...
  }

  // Update severity / team / assignee
  async function updateSeverity(incidentId, newSeverity) {
    // ...
  }
  async function updateTeam(incidentId, newTeam) {
    // ...
  }
  async function updateAssignee(incidentId, newAssignee) {
    // ...
  }
  async function linkMainAlert(incidentId, mainAlertId) {
    // ...
  }
</script>

<svelte:head>
  <!-- Bootstrap CSS & Bootstrap Icons -->
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css"
    crossorigin="anonymous"
  />
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
  />
  <style>
    body {
      background-color: #f0f2f5;
    }
    /* Dark mode styles */
    body.dark-mode {
      background-color: #333;
      color: #eee;
    }
    body.dark-mode .incident-box {
      background-color: #444;
      border-color: #555;
    }
    body.dark-mode .main-alert-box {
      background-color: #555;
      border-color: #777;
    }
    body.dark-mode .comment-box {
      background-color: #555;
      border-color: #777;
    }

    /* Dark mode for form controls and dropdowns */
    body.dark-mode .form-control {
      background-color: #555;
      border-color: #777;
      color: #eee;
    }
    body.dark-mode .form-control::placeholder {
      color: #ccc;
    }
    body.dark-mode select.form-control {
      background-color: #555;
      border-color: #777;
      color: #eee;
    }
    body.dark-mode .dropdown-menu {
      background-color: #444;
      border-color: #666;
      color: #eee;
    }
    body.dark-mode .dropdown-item {
      background-color: #444;
      color: #eee;
    }
    body.dark-mode .dropdown-item:hover {
      background-color: #555;
    }

    .container-custom {
      max-width: 1500px;
      margin: 0 auto;
    }
    .incident-box {
      border: 1px solid #ddd;
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 1rem;
      background-color: #ffffff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .global-controls button {
      margin-right: 0.5rem;
    }
    /* Style dropdown triggers as plain text matching label style */
    .dropdown-text {
      background: none;
      border: none;
      padding: 0;
      margin: 0 2px;
      font-family: inherit;
      font-size: inherit;
      color: inherit;
      cursor: pointer;
    }
    /* Force dropdown menu to display block when rendered */
    .dropdown-menu {
      display: block;
      background: white;
      border: 1px solid #ccc;
      border-radius: 0.25rem;
      padding: 4px 0;
      position: absolute;
      z-index: 10;
      min-width: 80px;
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
    /* Inline title editing styles */
    .title-text {
      cursor: pointer;
      font-size: 1rem;
      font-weight: bold;
    }
    .title-input {
      font-size: 1rem;
      font-weight: bold;
      border: none;
      outline: none;
      background: rgba(255,255,255,0.9);
    }
  </style>
</svelte:head>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <a
    class="navbar-brand"
    href="/"
    on:click|preventDefault
    on:keydown={(e) => handleKeyAction(e, () => {})}
  >
    Incident Management
  </a>
  <button
    class="navbar-toggler"
    type="button"
    data-toggle="collapse"
    data-target="#navbarContent"
    aria-controls="navbarContent"
    aria-expanded="false"
    aria-label="Toggle navigation"
  >
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="collapse navbar-collapse" id="navbarContent">
    <!-- Left side navbar items -->
    <ul class="navbar-nav mr-auto">
      <li class="nav-item">
        <a
          class="nav-link"
          href="/"
          on:click|preventDefault
          on:keydown={(e) => handleKeyAction(e, () => {})}
        >
          Home
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          href="/"
          on:click|preventDefault
          on:keydown={(e) => handleKeyAction(e, () => {})}
        >
          About
        </a>
      </li>
    </ul>

    <!-- Right side icon buttons (aligned with ml-auto) -->
    <div class="ml-auto d-flex align-items-center">
      <!-- Undo -->
      <button
        on:click={undoAction}
        class="btn btn-secondary mr-2"
        aria-label="Undo"
      >
        <i class="bi bi-arrow-counterclockwise"></i>
      </button>

      <!-- Redo -->
      <button
        on:click={redoAction}
        class="btn btn-secondary mr-2"
        aria-label="Redo"
      >
        <i class="bi bi-arrow-clockwise"></i>
      </button>

      <!-- Dark Mode -->
      <button
        class="btn btn-secondary mr-2"
        on:click={toggleDarkMode}
        aria-label="Dark Mode Toggle"
      >
        {#if darkMode}
          <i class="bi bi-sun-fill"></i>
        {:else}
          <i class="bi bi-sun"></i>
        {/if}
      </button>

      <!-- Notifications Toggle -->
      <button
        class="btn btn-secondary mr-2"
        on:click={toggleNotifications}
        aria-label="Notifications Toggle"
      >
        {#if darkMode}
          {#if notificationsOn}
            <!-- Dark mode + ON => bell-fill -->
            <i class="bi bi-bell-fill"></i>
          {:else}
            <!-- Dark mode + OFF => bell-slash-fill -->
            <i class="bi bi-bell-slash-fill"></i>
          {/if}
        {:else}
          {#if notificationsOn}
            <!-- Normal mode + ON => bell -->
            <i class="bi bi-bell"></i>
          {:else}
            <!-- Normal mode + OFF => bell-slash -->
            <i class="bi bi-bell-slash"></i>
          {/if}
        {/else}
      </button>

      <!-- User Profile Dropdown & Logout -->
      <div class="dropdown">
        <button
          class="btn btn-secondary dropdown-toggle"
          type="button"
          on:click={() => (showUserMenu = !showUserMenu)}
          aria-label="User Menu"
        >
          {userProfile.fullName}
        </button>

        {#if showUserMenu}
          <div class="dropdown-menu dropdown-menu-right">
            <h6 class="dropdown-header">Profile Info</h6>
            <span class="dropdown-item-text">
              Full Name: {userProfile.fullName}
            </span>
            <span class="dropdown-item-text">Role: {userProfile.role}</span>
            <span class="dropdown-item-text">
              App Version: {userProfile.appVersion}
            </span>
            {#if userProfile.role === "Admin"}
              <a class="dropdown-item" href="/">Admin URL</a>
            {/if}
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" on:click={logout}>Logout</button>
          </div>
        {/if}
      </div>
    </div>
  </div>
</nav>

<div class="container container-custom">
  <!-- New Alert Section -->
  <div class="mb-4 comment-box">
    <form on:submit|preventDefault={createAlert}>
      <div class="form-group">
        <label for="alert-name">New Alert:</label>
        <input
          id="alert-name"
          class="form-control"
          bind:value={newAlertName}
          placeholder="Enter alert message"
        />
      </div>
      <button type="submit" class="btn btn-success">Create Alert</button>
    </form>
  </div>

  <!-- Filter Section -->
  <div class="mb-4">
    <div class="form-row">
      <div class="form-group col-md-3">
        <label for="filter-status">Status:</label>
        <select
          id="filter-status"
          class="form-control"
          bind:value={statusFilter}
          on:change={onStatusChange}
        >
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
          <option value="all">All (open &amp; resolved)</option>
        </select>
      </div>
      <div class="form-group col-md-3">
        <label for="filter-team">Team:</label>
        <select
          id="filter-team"
          class="form-control"
          bind:value={teamFilter}
          on:change={onTeamChange}
        >
          <option value="">--Any--</option>
          <option value="team1">team1</option>
          <option value="team2">team2</option>
          <option value="team3">team3</option>
        </select>
      </div>
      <div class="form-group col-md-3">
        <label for="filter-assignee">Assignee:</label>
        <select
          id="filter-assignee"
          class="form-control"
          bind:value={assigneeFilter}
          on:change={onAssigneeChange}
        >
          <option value="">--Any--</option>
          <option value="person1">person1</option>
          <option value="person2">person2</option>
          <option value="person3">person3</option>
          <option value="person4">person4</option>
        </select>
      </div>
      <div class="form-group col-md-3">
        <label for="filter-severity">Severity:</label>
        <select
          id="filter-severity"
          class="form-control"
          bind:value={severityFilter}
          on:change={onSeverityChange}
        >
          <option value="">--Any--</option>
          <option value="MAJOR">MAJOR</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Global Controls -->
  <div class="global-controls mb-4">
    <button on:click={toggleAllIncidents} class="btn btn-primary m-2">
      {allIncidentsCollapsed ? "Expand All Incidents" : "Collapse All Incidents"}
    </button>
    <button on:click={toggleAllMainAlerts} class="btn btn-info m-2">
      {allMainAlertsCollapsed ? "Expand All Main Alerts" : "Collapse All Main Alerts"}
    </button>
    <button on:click={toggleAllComments} class="btn btn-warning m-2">
      {allCommentsCollapsed ? "Expand All Comments" : "Collapse All Comments"}
    </button>
    <button on:click={selectAllIncidents} class="btn btn-secondary m-2">Select All Incidents</button>
    {#if statusFilter === "resolved" || statusFilter === "all"}
      <button on:click={bulkReopenIncidents} class="btn btn-success m-2">
        Bulk Reopen Selected Incidents
      </button>
    {/if}
    {#if statusFilter === "open" || statusFilter === "all"}
      <button on:click={bulkResolveIncidents} class="btn btn-danger m-2">
        Bulk Resolve Selected Incidents
      </button>
    {/if}
  </div>

  <!-- Bulk Link Section -->
  <div class="mb-4">
    <form on:submit|preventDefault={() => bulkLinkMainAlerts(bulkTargetIncidentId)}>
      <div class="form-row">
        <div class="form-group col-md-4">
          <input
            type="number"
            id="bulk-target"
            class="form-control"
            bind:value={bulkTargetIncidentId}
            placeholder="Enter target incident ID"
          />
        </div>
        <div class="form-group col-md-4 align-self-end">
          <button type="submit" class="btn btn-secondary">Bulk Link Selected Main Alerts</button>
        </div>
      </div>
    </form>
  </div>

  <!-- Incident List -->
  <div class="row">
    {#each incidents as inc (inc.id)}
      <article
        class="col-12 incident-box"
        draggable="true"
        on:dragstart={(e) => handleIncidentDragStart(e, inc)}
        on:drop={(e) => handleIncidentDrop(e, inc.id)}
        on:dragover={allowDrop}
      >
        <!-- Incident Header: Always visible -->
        <header>
          <!-- Top Row: Incident Details & Action Buttons with Custom Dropdowns -->
          <div class="row align-items-center">
            <div class="col">
              <div class="d-flex flex-wrap align-items-center">
                <div class="mr-3">
                  <input
                    type="checkbox"
                    bind:checked={inc.selectedForBulk}
                    aria-label="Select incident for bulk actions"
                  />
                </div>
                <div class="mr-3"><strong>#{inc.id}</strong></div>
                <div class="mr-3">
                  <small><strong>Status:</strong> {inc.status}</small>
                </div>
                <div class="mr-3" style="position: relative;">
                  <small><strong>Severity:</strong></small>
                  <button
                    type="button"
                    class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Severity")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Severity"))}
                    aria-haspopup="true"
                    aria-expanded={inc.showSeverityDropdown}
                  >
                    {inc.severity}
                  </button>
                  {#if inc.showSeverityDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateSeverity(inc.id, "MAJOR");
                          inc.showSeverityDropdown = false;
                        }}
                      >
                        MAJOR
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateSeverity(inc.id, "HIGH");
                          inc.showSeverityDropdown = false;
                        }}
                      >
                        HIGH
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateSeverity(inc.id, "MEDIUM");
                          inc.showSeverityDropdown = false;
                        }}
                      >
                        MEDIUM
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateSeverity(inc.id, "LOW");
                          inc.showSeverityDropdown = false;
                        }}
                      >
                        LOW
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3" style="position: relative;">
                  <small><strong>Team:</strong></small>
                  <button
                    type="button"
                    class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Team")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Team"))}
                    aria-haspopup="true"
                    aria-expanded={inc.showTeamDropdown}
                  >
                    {inc.team}
                  </button>
                  {#if inc.showTeamDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateTeam(inc.id, "team1");
                          inc.showTeamDropdown = false;
                        }}
                      >
                        team1
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateTeam(inc.id, "team2");
                          inc.showTeamDropdown = false;
                        }}
                      >
                        team2
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateTeam(inc.id, "team3");
                          inc.showTeamDropdown = false;
                        }}
                      >
                        team3
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateTeam(inc.id, "team_overkoepelend");
                          inc.showTeamDropdown = false;
                        }}
                      >
                        team overkoepelend
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3" style="position: relative;">
                  <small><strong>Assignee:</strong></small>
                  <button
                    type="button"
                    class="dropdown-text ml-1"
                    on:click={() => toggleDropdown(inc, "Assignee")}
                    on:keydown={(e) => handleKeyAction(e, () => toggleDropdown(inc, "Assignee"))}
                    aria-haspopup="true"
                    aria-expanded={inc.showAssigneeDropdown}
                  >
                    {inc.assignee}
                  </button>
                  {#if inc.showAssigneeDropdown}
                    <div class="dropdown-menu" role="menu">
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateAssignee(inc.id, "person1");
                          inc.showAssigneeDropdown = false;
                        }}
                      >
                        person1
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateAssignee(inc.id, "person2");
                          inc.showAssigneeDropdown = false;
                        }}
                      >
                        person2
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateAssignee(inc.id, "person3");
                          inc.showAssigneeDropdown = false;
                        }}
                      >
                        person3
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        on:click={() => {
                          updateAssignee(inc.id, "person4");
                          inc.showAssigneeDropdown = false;
                        }}
                      >
                        person4
                      </button>
                    </div>
                  {/if}
                </div>
                <div class="mr-3"><small><strong>Alerts:</strong> {inc.alert_count}</small></div>
                <div class="mr-3"><small><strong>Reopens:</strong> {inc.reopen_count}</small></div>
                <div class="mr-3"><small><strong>Wiki:</strong> {inc.wiki_url}</small><br /></div>
              </div>
            </div>
            <div class="col-auto">
              <div class="d-flex align-items-center">
                {#if inc.status === "open"}
                  <button
                    class="btn btn-sm btn-danger mr-2"
                    on:click={() => resolveIncident(inc.id)}
                  >
                    Resolve
                  </button>
                  <button
                    class="btn btn-sm btn-dark mr-2"
                    on:click={() => definitivelyResolveIncident(inc.id)}
                  >
                    Definitively Resolve
                  </button>
                {:else}
                  <button
                    class="btn btn-sm btn-success mr-2"
                    on:click={() => reopenIncident(inc.id)}
                  >
                    Reopen
                  </button>
                {/if}
                <button
                  class="btn btn-sm btn-outline-secondary"
                  on:click={() => toggleIncidentCollapse(inc)}
                >
                  {inc.collapsed ? "Expand" : "Collapse"}
                </button>
              </div>
            </div>
          </div>

          <!-- Lower Row: Title -->
          <div class="row mt-1 ml-5">
            <div class="col">
              {#if !inc.editingTitle}
                <span
                  class="title-text"
                  on:click={() => {
                    inc.editingTitle = true;
                    inc.renameText = inc.incident_name;
                    incidents = [...incidents];
                  }}
                >
                  {inc.incident_name}
                </span>
              {:else}
                <input
                  type="text"
                  class="title-input"
                  bind:value={inc.renameText}
                  autofocus
                  on:blur={() => submitTitle(inc)}
                  on:keydown={(e) => {
                    if (e.key === "Enter") {
                      submitTitle(inc);
                    }
                  }}
                />
              {/if}
              <br />
            </div>
          </div>
        </header>

        <!-- Expanded View: Main Alerts Section & Comments -->
        {#if !inc.collapsed}
          <section class="incident-extra">
            <!-- Main Alerts Section -->
            {#if inc.showMainAlerts}
              <div class="mt-2 p-2 border rounded main-alert-box" role="region" aria-label="Main Alerts">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="h6 m-0">Main Alerts</h5>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    on:click={() => toggleMainAlerts(inc)}
                  >
                    Hide Main Alerts
                  </button>
                </div>
                {#if inc.main_alerts && inc.main_alerts.length > 0}
                  <ul class="list-unstyled mb-0 mt-2">
                    {#each inc.main_alerts as ma}
                      <li
                        class="mb-1 d-flex align-items-center"
                        draggable="true"
                        on:dragstart={(e) => handleDragStart(e, ma, inc.id)}
                      >
                        <input
                          type="checkbox"
                          bind:checked={ma.selectedForBulk}
                          aria-label="Select main alert"
                          class="mr-2"
                        />
                        <span>
                          <strong>ID:</strong> {ma.id}
                          {" | "}
                          <strong>Message:</strong> {ma.message}
                          {" | "}
                          <strong>Counter:</strong> {ma.counter}
                          {" | "}
                          <strong>Last Alert:</strong> {ma.last_linked_time}
                        </span>
                      </li>
                    {/each}
                  </ul>
                {:else}
                  <p class="mb-0 mt-2">No main alerts available.</p>
                {/if}
              </div>
            {:else}
              <button
                class="btn btn-sm btn-outline-primary"
                on:click={() => toggleMainAlerts(inc)}
              >
                Show Main Alerts
              </button>
            {/if}

            <!-- Comments Section -->
            <div class="mb-3">
              {#if inc.showComments}
                <div class="mt-2 p-2 border rounded comment-box" role="region" aria-label="Comments">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="h6 m-0">Comments</h5>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-info"
                      on:click={() => toggleComments(inc)}
                    >
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
                          <div class="mb-1">
                            {@html comment.comment_text}
                          </div>
                          <div class="d-flex">
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-secondary mr-2"
                              on:click={() => editComment(inc, comment)}
                            >
                              Modify
                            </button>
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-danger"
                              on:click={() => deleteIncidentComment(inc.id, comment.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </li>
                      {/each}
                    </ul>
                  {:else}
                    <p class="mt-2">No comments available.</p>
                  {/if}
                  {#if !inc.showCommentEditor}
                    <div class="mt-3">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        on:click={() => {
                          inc.showCommentEditor = true;
                          inc.editingComment = null;
                          inc.newCommentText = "";
                          inc.newCommentLogin = "";
                          incidents = [...incidents];
                        }}
                      >
                        Add New Comment
                      </button>
                    </div>
                  {/if}
                  {#if inc.showCommentEditor}
                    <div class="mt-3">
                      <form on:submit|preventDefault={() => submitComment(inc)}>
                        <QuillEditor bind:content={inc.newCommentText} />
                        <div class="form-row align-items-center mt-2">
                          <div class="col-md-4">
                            <label for="comment-login-{inc.id}" class="sr-only">
                              Your Login Name
                            </label>
                            <input
                              type="text"
                              id="comment-login-{inc.id}"
                              class="form-control form-control-sm"
                              placeholder="Your login name"
                              bind:value={inc.newCommentLogin}
                            />
                          </div>
                          <div class="col-auto">
                            <button
                              type="submit"
                              class="btn btn-sm btn-success"
                            >
                              {inc.editingComment ? "Update Comment" : "Add Comment"}
                            </button>
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-secondary ml-2"
                              on:click={() => {
                                inc.showCommentEditor = false;
                                inc.editingComment = null;
                                inc.newCommentText = "";
                                inc.newCommentLogin = "";
                                incidents = [...incidents];
                              }}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      </form>
                    </div>
                  {/if}
                </div>
              {:else}
                <button
                  type="button"
                  class="btn btn-sm btn-outline-info mt-2"
                  on:click={() => toggleComments(inc)}
                >
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
