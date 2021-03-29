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
      {props.strings.map((l, i) => <Language key={`sb-${i}`} langid={i} language={l} hoverLang={props.hoverLang} examineString={props.examineString} />)}
      </ul>
    </div>
  )
}

function Language(props) {
  const vocab = [...new Set(props.language.reduce((acc, cur) => {
    return [...acc, ...cur.split(/[,|]+/).filter(v => v !== '')]
  }, []))]

  return (
    <li onMouseEnter={() => props.hoverLang(vocab)} onMouseLeave={() => props.hoverLang()} className="sb-language"><span className="sb-lbracket">[</span><div>{props.language.map((s, i) => <String examineString={props.examineString} key={`s-${props.langid}-${i}`}>{s}</String>)}</div><span className="sb-rbracket">]</span></li>
  )
}

function String(props) {
  return (
    <span onClick={() => props.examineString(props.children)} className="sb-string">{props.children}</span>
  )
}
