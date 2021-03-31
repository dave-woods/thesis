import { useRef } from 'react'

export default function TextDisplay(props) {
  const elem = useRef(null)

  return (
    <div className="text">
      <pre className={props.noHighlight ? 'no-highlight' : ''} dangerouslySetInnerHTML={{ __html: props.text}} ref={elem}></pre>
      <div className="btns">
        <button id="btn-new" onClick={props.reset}>New</button>
        <button id="btn-export" onClick={() => props.download(elem)}>Export</button>
      </div>
    </div>
  )
}
