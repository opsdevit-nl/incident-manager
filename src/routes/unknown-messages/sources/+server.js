/** @type {import('./$types').RequestHandler} */
export async function GET() {
    // Replace this with your database query if needed.
    const sources = ["app1", "app2", "app3"];
    return new Response(JSON.stringify({ sources }), {
      headers: { "Content-Type": "application/json" }
    });
  }