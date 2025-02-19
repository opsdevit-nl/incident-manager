/** @type {import('./$types').RequestHandler} */
export async function GET({ url }) {
  // Retrieve query parameters
  const host = url.searchParams.get("host") || "";
  const startDate = url.searchParams.get("startDate") || "";
  const endDate = url.searchParams.get("endDate") || "";
  const sourcesParam = url.searchParams.get("sources") || "";
  const sources = sourcesParam ? sourcesParam.split(",").map(s => s.trim()) : [];
  const filterWindows = url.searchParams.get("filter_windows") === "true";
  const filterLinux = url.searchParams.get("filter_linux") === "true";

  // Dummy data – replace with your database query logic
  const unknown_messages = [
    { id: 1, source: "app1", host: "host1", message: "Error A", ts: "2025-02-01T12:00:00Z" },
    { id: 2, source: "app1", host: "host1", message: "Error A", ts: "2025-02-01T12:05:00Z" },
    { id: 3, source: "app2", host: "host2", message: "Error B", ts: "2025-02-01T12:10:00Z" },
    { id: 4, source: "app4", host: "host2", message: "Error B", ts: "2025-02-01T12:10:00Z" },
    { id: 5, source: "app3", host: "host3", message: "Error B", ts: "2025-02-01T12:10:00Z" },
    { id: 6, source: "app5", host: "host3", message: "Error B", ts: "2025-02-01T12:10:00Z" },
    { id: 7, source: "app2", host: "host4", message: "Error B", ts: "2025-02-01T12:10:00Z" },
    { id: 8, source: "app3", host: "host5", message: "Error D", ts: "2025-02-01T12:10:00Z" }
  ];

  // Filter unknown messages
  const filtered = unknown_messages.filter(msg => {
    const hostMatch = host ? msg.host.includes(host) : true;
    const sourceMatch = sources.length ? sources.includes(msg.source) : true;
    let dateMatch = true;
    if (startDate) {
      dateMatch = dateMatch && (new Date(msg.ts) >= new Date(startDate));
    }
    if (endDate) {
      dateMatch = dateMatch && (new Date(msg.ts) <= new Date(endDate));
    }
    // (filterWindows and filterLinux could be used to exclude certain messages if needed)
    return hostMatch && sourceMatch && dateMatch;
  });

  return new Response(JSON.stringify({ unknown_messages: filtered }), {
    headers: { "Content-Type": "application/json" }
  });
}
