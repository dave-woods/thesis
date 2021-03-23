import { useState } from 'react'
export default function StringBank(props) {
  const [loading, setLoading] = useState(false)
  
  const doSuperposition = async () => {
    setLoading(true)
    fetch('/api/superpose', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          strings: props.strings,
          limit: 12
        }
      })
    }).then(resp => resp.json()).then(data => {
      setLoading(false)
      if (data.stderr) {
        window.alert(data.stderr)
      } else if (data.error) {
        // console.log(data.error)
      } else {
        props.updateStrings(JSON.parse(data.stdout))
      }
    })
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
