export const getFreksa = async (e1, e2, rel) => {
    return await fetch('/api/freksa', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: { e1, e2, rel }
      })
    })
}
