import { useState } from 'react'
export default function StringBank(props) {
  const [loading, setLoading] = useState(false)
  
  const doSuperposition = async () => {
    setLoading(true)
    // fetch('/api/superpose', {
    const res = await fetch(process.env.NEXT_PUBLIC_SUPERPOSE_ENDPOINT, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          strings: props.strings,
          limit: props.limit
        }
      })
    })
    setLoading(false)
    const data = await res.json()
    if (data.error) {
      console.error(data.error)
      window.alert(data.error)
    } else {
      props.updateStrings(data.strings)
    }
  }

  return (
    <div className="string-bank">
      <h4>String bank ({props.strings.length}) <button disabled={loading || props.strings.length < 2} id="dosp" onClick={doSuperposition}>Superpos{loading ? 'ing' : 'e'}</button></h4>
      <ul className="strings">
      {props.strings.map((s, i) => <li key={`es-${i}`}>[{s.join(',\n')}]</li>)}
      </ul>
    </div>
  )
}
