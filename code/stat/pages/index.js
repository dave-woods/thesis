import { useState, useRef, useEffect, useCallback, userReducer } from 'react'
import Head from 'next/head'

import { parseTML } from '../fns/parseTML'
import { getFreksa } from '../fns/getFreksa'

import Details from '../components/Details'
import Help from '../components/Help'
import StringBank from '../components/StringBank'
import CreateRelation from '../components/CreateRelation'
import TextEntry from '../components/TextEntry'
import TextDisplay from '../components/TextDisplay'
import EventList from '../components/EventList'

export default function Annotate() {
  const [helpDisplayed, setHelpDisplayed] = useState(false)
  const [detailsPaneDisplayed, setDetailsPaneDisplayed] = useState(false)
  const [textHTML, setTextHTML] = useState('')
  const [parsedTlinks, setParsedTlinks] = useState([])
  const [parsedEvents, setParsedEvents] = useState([])
  const [eventStrings, setEventStrings] = useState([])
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

  const grabParse = (textareaValue) => {
    if (textareaValue.trim() !== '') {
      const parseResult = parseTML(textareaValue)
      if (parseResult.transformed) {
        setTextHTML(parseResult.transformed)
        setParsedTlinks([...parseResult.tlinks])
        setParsedEvents([...parseResult.events])
        parseResult.tlinks.forEach(async tlink => {
          const res = await getFreksa(tlink.e1, tlink.e2, tlink.rel)
          const data = await res.json()
          setEventStrings(prev => [JSON.parse(data.stdout), ...prev])
        })
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


  const testRelation = async (e1, e2, rel) => {
    fetch('/api/test', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          strings: eventStrings,
          e1,
          e2,
          rel
        }
      })
    }).then(response => response.json()).then(data => {
      const { status, strings } = JSON.parse(data.stdout)
      window.alert(`That relation is ${status} according to the knowledge base.${status !== 'contradicted' ? `\nClick 'Add New Relation' to add:\n${strings}` : ''}`)
    })
  }

  return (
    <main id="annotate">
      <Head><title>String Temporal Annotation Tool</title></Head>
      {helpDisplayed && <Help dismiss={dismissOverlay} />}
      {detailsPaneDisplayed && <Details dismiss={dismissOverlay} />}
      {!textHTML ? <TextEntry grabParse={grabParse}/> : <TextDisplay text={textHTML} reset={() => setTextHTML('')}/>}
      <div className="panel">
        <p>Select some text, then tag as Event or Time</p>
        <div className="btns">
          <button id="btn-undo">Undo</button>
          <button id="btn-reset">Reset</button>
          <button id="btn-tag-event" onClick={() => createMark('EVENT')}>Tag Event</button>
          <button id="btn-tag-time" onClick={() => createMark('TIMEX3')}>Tag Time</button>
          <button id="btn-help" onClick={() => setHelpDisplayed(true)}>Help</button>
        </div>
        <EventList events={parsedEvents} />
      </div>
      <StringBank strings={eventStrings} updateStrings={res => setEventStrings([...res])}/>
      {parsedEvents.length > 0 ? <CreateRelation events={parsedEvents} addRelation={res => setEventStrings(prev => [res, ...prev])} testRelation={testRelation}/> : <div className="relations"></div>}
    </main>
  )
}
