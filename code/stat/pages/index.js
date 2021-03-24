import { useState, useRef, useEffect, useCallback, useReducer } from 'react'
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
  // const [textHTML, setTextHTML] = useState('')
  // const [parsedTlinks, setParsedTlinks] = useState([])
  // const [parsedEvents, setParsedEvents] = useState([])
  // const [eventStrings, setEventStrings] = useState([])
  // const [nextId, setNextId] = useState(1)

  const initialState = {
    textHTML: '',
    parsedTlinks: [],
    parsedEvents: [],
    eventStrings: [],
    nextId: 1,
    prevStates: []
  }

  const init = initialObj => ({
    ...initialObj
  })

  const [state, dispatch] = useReducer((curState, action) => {
    switch (action.type) {
      case 'SET_TEXT':
        return {
          ...curState,
          textHTML: action.payload,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'SET_TLINKS':
        return {
          ...curState,
          parsedTlinks: action.payload,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'SET_EVENTS':
        return {
          ...curState,
          parsedEvents: action.payload,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'ADD_EVENTS':
        return {
          ...curState,
          parsedEvents: [...curState.parsedEvents, action.payload],
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'SET_STRINGS':
        return {
          ...curState,
          eventStrings: action.payload,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'ADD_STRINGS':
        return {
          ...curState,
          eventStrings: [action.payload, ...curState.eventStrings],
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'SET_NEXTID':
        return {
          ...curState,
          nextId: action.payload,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'UNDO': 
        const [cur, ...pre] = curState.prevStates
        // console.log('undo')
        return {
          ...cur,
          prevStates: pre
        }
      default:
        throw new Error('Undefined action type.')
    }
  }, initialState, init)

  useEffect(() => {
    document.addEventListener('keyup', handleKeyboard, false)
      return () => {
        document.removeEventListener('keyup', handleKeyboard, false)
      }
  // }, [helpDisplayed, detailsPaneDisplayed, nextId])
  }, [helpDisplayed, detailsPaneDisplayed, state.nextId])

  const handleKeyboard = useCallback(e => {
    const kb = e.key.toLowerCase()
      if (kb === 'e') {
        createMark('EVENT')
      } else if (kb === 't') {
        createMark('TIMEX3')
      } else if (kb === 'u') {
        // undo()
        dispatch({type: 'UNDO'})
      } else if (kb === '?') {
        setHelpDisplayed(!helpDisplayed)
      } else if (kb === 'escape') {
        setHelpDisplayed(false)
        setDetailsPaneDisplayed(false)
      }
  // }, [helpDisplayed, detailsPaneDisplayed, nextId])
  }, [helpDisplayed, detailsPaneDisplayed, state.nextId])

  const grabParse = (textareaValue) => {
    if (textareaValue.trim() !== '') {
      const parseResult = parseTML(textareaValue)
      if (parseResult.transformed) {
        // setTextHTML(parseResult.transformed)
        // setParsedTlinks([...parseResult.tlinks])
        // setParsedEvents([...parseResult.events])
        dispatch({type: 'SET_TEXT', payload: parseResult.transformed})
        dispatch({type: 'SET_TLINKS', payload: [...parseResult.tlinks]})
        dispatch({type: 'SET_EVENTS', payload: [...parseResult.events]})
        parseResult.tlinks.forEach(async tlink => {
          const res = await getFreksa(tlink.e1, tlink.e2, tlink.rel)
          const data = await res.json()
          // setEventStrings(prev => [JSON.parse(data.stdout), ...prev])
          dispatch({type: 'ADD_STRINGS', payload: JSON.parse(data.stdout)})
        })
      } else {
        // setTextHTML(parseResult.imported)
        dispatch({type: 'SET_TEXT', payload: parseResult.imported})
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
    // let sortedIds = parsedEvents.map(ev => parseInt(ev.id.substring(1)))
    let sortedIds = state.parsedEvents.map(ev => parseInt(ev.id.substring(1)))
    sortedIds.sort((a, b) => a - b)
    // setNextId(prev => (sortedIds[sortedIds.length - 1] || prev) + 1)
    dispatch({type: 'SET_NEXTID', payload: (sortedIds[sortedIds.length - 1] || state.nextId) + 1})
  // }, [parsedEvents])
  }, [state.parsedEvents])

  const createMark = useCallback(tag => {
    if (window.getSelection) {
      const sel = window.getSelection()
      if (sel.type === 'Range' && sel.anchorNode === sel.focusNode && sel.anchorNode.parentElement === document.querySelector('.text pre') && sel.toString().trim() !== '') {
        if (sel.rangeCount) {
          const wrapEl = document.createElement('span')
          wrapEl.classList.add('tml-ev-ano', tag)
          if (tag === 'EVENT') {
            // wrapEl.dataset.id = `e${nextId}`
            wrapEl.dataset.id = `e${state.nextId}`
            wrapEl.dataset.eventClass = 'OCCURRENCE'
          } else {
            // wrapEl.dataset.id = `t${nextId}`
            wrapEl.dataset.id = `t${state.nextId}`
            wrapEl.dataset.type = 'DATE'
          }
          wrapEl.textContent = sel.toString()
          const range = sel.getRangeAt(0).cloneRange()
          range.deleteContents()
          range.insertNode(wrapEl)
          sel.removeAllRanges()
          sel.addRange(range)
          // setParsedEvents(prev => [...prev, {
          dispatch({type: 'ADD_EVENTS', payload: {
            id: wrapEl.dataset.id,
            type: tag,
            text: wrapEl.textContent,
            attr: {}
          }})
        }
      }
    }
  // }, [nextId])
  }, [state.nextId])


  const testRelation = async (e1, e2, rel) => {
    fetch('/api/test', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          // strings: eventStrings,
          strings: state.eventStrings,
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
      {!state.textHTML ? <TextEntry grabParse={grabParse}/> : <TextDisplay text={state.textHTML} reset={() => dispatch({type: 'SET_TEXT', payload: ''})}/>}
      <div className="panel">
        <p>Select some text, then tag as Event or Time</p>
        <div className="btns">
          <button id="btn-undo">Undo</button>
          <button id="btn-reset">Reset</button>
          <button id="btn-tag-event" onClick={() => createMark('EVENT')}>Tag Event</button>
          <button id="btn-tag-time" onClick={() => createMark('TIMEX3')}>Tag Time</button>
          <button id="btn-help" onClick={() => setHelpDisplayed(true)}>Help</button>
        </div>
        <EventList events={state.parsedEvents} />
      </div>
      <StringBank strings={state.eventStrings} updateStrings={res => dispatch({type: 'SET_STRINGS', payload: [...res]})}/>
      {state.parsedEvents.length > 0 ? <CreateRelation events={state.parsedEvents} addRelation={res => dispatch({type: 'ADD_STRINGS', payload: res})} testRelation={testRelation}/> : <div className="relations"></div>}
    </main>
  )
}
