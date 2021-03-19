import { useState, useRef, useEffect, useCallback } from 'react'
import Head from 'next/head'

import { parseTML } from '../fns/parseTML'

export default function Annotate() {
  const [helpDisplayed, setHelpDisplayed] = useState(false)
  const [detailsPaneDisplayed, setDetailsPaneDisplayed] = useState(false)
  const [textareaValue, setTextareaValue] = useState('')
  const [textHTML, setTextHTML] = useState('')
  const [parsedTlinks, setParsedTlinks] = useState([])
  const [parsedEvents, setParsedEvents] = useState([])
  const [nextId, setNextId] = useState(1)

  useEffect(() => {
    document.addEventListener('keyup', handleKeyboard, false)
      return () => {
        document.removeEventListener('keyup', handleKeyboard, false)
      }
  }, [helpDisplayed, detailsPaneDisplayed, nextId])

  const handleKeyboard = useCallback(e => {
    const kb = e.key.toLowerCase()
      if (kb === 'e') {
        createMark('EVENT')
      } else if (kb === 't') {
        createMark('TIMEX3')
      } else if (kb === 'u') {
        // undo()
      } else if (kb === '?') {
        setHelpDisplayed(!helpDisplayed)
      } else if (kb === 'escape') {
        setHelpDisplayed(false)
          setDetailsPaneDisplayed(false)
      }
  }, [helpDisplayed, detailsPaneDisplayed, nextId])

  const handleTextarea = useCallback(e => {
    setTextareaValue(e.target.value)
  }, [textareaValue])

  const grabParse = () => {
    if (textareaValue.trim() !== '') {
      const parseResult = parseTML(textareaValue)
        if (parseResult.transformed) {
          setTextHTML(parseResult.transformed)
            setParsedTlinks([...parseResult.tlinks])
            setParsedEvents([...parseResult.events])
        } else {
          setTextHTML(parseResult.imported)
        }
    }
  }

  const dismissOverlay = e => {
    e.stopPropagation()
      if (e.currentTarget === e.target) {
        setHelpDisplayed(false)
          setDetailsPaneDisplayed(false)
      }
  }

  const firstUpdate = useRef(true)
  useEffect(() => {
    if (firstUpdate.current) {
      firstUpdate.current = false
      return
    }
    let sortedIds = parsedEvents.map(ev => parseInt(ev.id.substring(1)))
    sortedIds.sort((a, b) => a - b)
    setNextId(prev => (sortedIds[sortedIds.length - 1] || prev) + 1)
  }, [parsedEvents])

  const createMark = useCallback(tag => {
    if (window.getSelection) {
      const sel = window.getSelection()
      if (sel.type === 'Range' && sel.anchorNode === sel.focusNode && sel.anchorNode.parentElement === document.querySelector('.text pre') && sel.toString().trim() !== '') {
        if (sel.rangeCount) {
          const wrapEl = document.createElement('span')
          wrapEl.classList.add('tml-ev-ano', tag)
          if (tag === 'EVENT') {
            wrapEl.dataset.id = `e${nextId}`
            wrapEl.dataset.eventClass = 'OCCURRENCE'
          } else {
            wrapEl.dataset.id = `t${nextId}`
            wrapEl.dataset.type = 'DATE'
          }
          wrapEl.textContent = sel.toString()
          const range = sel.getRangeAt(0).cloneRange()
          range.deleteContents()
          range.insertNode(wrapEl)
          sel.removeAllRanges()
          sel.addRange(range)
          setParsedEvents(prev => [...prev, {
            id: wrapEl.dataset.id,
            type: tag,
            text: wrapEl.textContent,
            attr: {}
          }])
        }
      }
    }
  }, [nextId])

  return (
    <main id="annotate">
      <Head>
        <title>String Temporal Annotation Tool</title>
      </Head>
      {helpDisplayed && <div className="help-wrap" onClick={dismissOverlay}>
        <div className="help">
          <h3>TimeML Annotation</h3>
          <p>
            Use the mouse to highlight text, then press 'Tag Event' to tag that text as an event, or press 'Tag Time' to tag that text as a time.
          </p>
          <p>
            Keyboard shortcuts:
          </p>
          <ul>
            <li>E: Tag Event</li>
            <li>T: Tag Time</li>
            <li>U: Undo</li>
            <li>?: Toggle Help</li>
          </ul>
        </div>
      </div>}
      {detailsPaneDisplayed && <div className="add-details-wrap" onClick={dismissOverlay}>
        <div className="add-details">
          <h3>Add attributes</h3>
          <div className="event-attr">
            Class: <select>
              <option value="OCCURRENCE">OCCURRENCE</option>
              <option value="PERCEPTION">PERCEPTION</option>
              <option value="REPORTING">REPORTING</option>
              <option value="ASPECTUAL">ASPECTUAL</option>
              <option value="STATE">STATE</option>
              <option value="I_STATE">I_STATE</option>
              <option value="I_ACTION">I_ACTION</option>
            </select>
            <button className="update-attr">Update</button>
          </div>
          <div className="time-attr">
            Type: <select>
              <option value="DATE">DATE</option>
              <option value="TIME">TIME</option>
              <option value="DURATION">DURATION</option>
              <option value="SET">SET</option>
            </select>
            <button className="update-attr">Update</button>
          </div>
        </div>
      </div>}
      {!textHTML ? <div className="input-text">
        <textarea value={textareaValue} onChange={handleTextarea} placeholder="Enter text or a TimeML file to annotate"></textarea>
          <div className="btns">
          <button onClick={grabParse}>Annotate</button> <a href="https://www.scss.tcd.ie/~dwoods/thesis/code/example.tml">Sample</a>
          </div>
          </div>
          :
          <div className="text">
          <pre dangerouslySetInnerHTML={{ __html: textHTML}}></pre>
          <div className="btns">
          <button id="btn-new" onClick={() => setTextHTML(null)}>New</button>
          <button id="btn-export">Export</button>
          </div>
          </div>}
      <div className="panel">
        <p>Select some text, then tag as Event or Time {nextId}</p>
        <div className="btns">
        <button id="btn-undo">Undo</button>
        <button id="btn-reset">Reset</button>
        <button id="btn-tag-event" onClick={() => createMark('EVENT')}>Tag Event</button>
        <button id="btn-tag-time" onClick={() => createMark('TIMEX3')}>Tag Time</button>
        <button id="btn-help" onClick={() => setHelpDisplayed(true)}>Help</button>
        </div>
        <ul className="event-list">
        {parsedEvents.map(ev => <li key={ev.id}>{ev.id}: {ev.text}</li>)}
        </ul>
        </div>
        <div className="string-bank">
        <h4>String bank <button disabled id="dosp">Superpose</button></h4>
        <ul className="strings"></ul>
        </div>
        <div className="relations">
        <div>
        <select className="ev1"></select> is <select className="rel">
        <option value="b">BEFORE (|a||b|)</option>
        <option value="bi">AFTER (|b||a|)</option>
        <option value="m">MEETING (|a|b|)</option>
        <option value="mi">MET BY (|b|a|)</option>
        <option value="s">STARTING (|a,b|b|)</option>
        <option value="si">STARTED BY (|a,b|a|)</option>
        <option value="f">FINISHING (|b|a,b|)</option>
        <option value="fi">FINISHED BY (|a|a,b|)</option>
        <option value="di">CONTAINING (|a|a,b|a|)</option>
        <option value="d">CONTAINED BY (|b|a,b|b|)</option>
        <option value="o">OVERLAPPING (|a|a,b|b|)</option>
        <option value="oi">OVERLAPPED BY (|b|a,b|a|)</option>
        <option value="e">EQUAL TO (|a,b|)</option>
        </select> <select className="ev2"></select></div>
        <button id="createRelation">Set</button>
        </div>
        </main>
        )
}
