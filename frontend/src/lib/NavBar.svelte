<script>
    export let userProfile = { fullName: "John Doe", role: "Admin", appVersion: "1.0.0" };
    export let darkMode = false;
    export let undoAction = () => {};
    export let redoAction = () => {};
    export let toggleDarkMode = () => {};
    export let logout = () => {};
  </script>
  
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <a class="navbar-brand" href="/">Infra Incident Management</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarContent" 
            aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarContent">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item"><a class="nav-link" href="/">Incidents</a></li>
        <li class="nav-item"><a class="nav-link" href="/unknown-messages/">Unknown Messages</a></li>
      </ul>
      <div class="ml-auto d-flex align-items-center">
        <button on:click={() => { console.log("Undo button clicked"); undoAction(); }} 
                class="btn btn-secondary mr-2" aria-label="Undo">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
        <button on:click={() => { console.log("Redo button clicked"); redoAction(); }} 
                class="btn btn-secondary mr-2" aria-label="Redo">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <button on:click={() => toggleDarkMode()} 
                class="btn btn-secondary mr-2" aria-label="Dark Mode Toggle">
          {#if darkMode} <i class="bi bi-sun-fill"></i> {:else} <i class="bi bi-sun"></i> {/if}
        </button>
        <button on:click={() => logout()} class="btn btn-secondary mr-2">Logout</button>
      </div>
    </div>
  </nav>
  