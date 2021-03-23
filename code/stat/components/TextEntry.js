import { useState, useCallback } from 'react'

export default function TextEntry(props) {
  const [textareaValue, setTextareaValue] = useState('')
  const handleTextarea = useCallback(e => {
    setTextareaValue(e.target.value)
  }, [textareaValue])

  return (
    <div className="input-text">
      <textarea value={textareaValue} onChange={handleTextarea} placeholder="Enter text or a TimeML file to annotate"></textarea>
      <div className="btns">
        <button onClick={() => { props.grabParse(textareaValue) }}>Annotate</button> <a href="https://www.scss.tcd.ie/~dwoods/thesis/code/example.tml">Sample</a>
      </div>
    </div>
  )
}
