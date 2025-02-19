<script>
  import { onMount } from 'svelte';
  export let content = ""; // enable binding from parent

  let editorDiv;
  let quill;

  onMount(async () => {
    const { default: Quill } = await import('quill');
    quill = new Quill(editorDiv, {
      theme: 'snow',
      modules: {
        toolbar: [
          ['bold', 'italic', 'underline'],
          [{ header: [1, 2, false] }],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['clean']
        ]
      }
    });

    // Initialize with the bound content if provided.
    quill.root.innerHTML = content;

    // Update bound "content" whenever the editor changes.
    quill.on('text-change', () => {
      content = quill.root.innerHTML;
    });
  });
</script>

<div bind:this={editorDiv} style="height: 200px;"></div>

<style>
  @import "https://cdn.quilljs.com/1.3.6/quill.snow.css";
</style>