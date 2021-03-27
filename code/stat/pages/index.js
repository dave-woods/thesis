import { useState, useRef, useEffect, useCallback, useReducer } from 'react'
import Head from 'next/head'

import { parseTML } from '../fns/parseTML'
import * as freksa from '../fns/freksa'

import Details from '../components/Details'
import Help from '../components/Help'
import StringBank from '../components/StringBank'
import CreateRelation from '../components/CreateRelation'
import TextEntry from '../components/TextEntry'
import TextDisplay from '../components/TextDisplay'
import EventList from '../components/EventList'

export default function Annotate() {
  const [helpDisplayed, setHelpDisplayed] = useState(false)
  const [details, setDetails] = useState(null)
  const [superposeLimit, setSuperposeLimit] = useState(12)
  const [extendedRels, setExtendedRels] = useState(false)

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
    const getLastId = (evs, curId) => {
      let sortedIds = evs.map(ev => parseInt(ev.id.substring(1)))
      sortedIds.sort((a, b) => a - b)
      return (sortedIds[sortedIds.length - 1] || curId)
    }
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
          nextId: getLastId(action.payload, curState.nextId) + 1,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'ADD_EVENT':
        return {
          ...curState,
          parsedEvents: [...curState.parsedEvents, action.payload.event],
          textHTML: action.payload.newText,
          nextId: getLastId([...curState.parsedEvents, action.payload.event], curState.nextId) + 1,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'REMOVE_EVENT':
        return {
          ...curState,
          parsedEvents: curState.parsedEvents.filter(e => e.id !== action.payload.id),
          textHTML: action.payload.newText,
          prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
        }
      case 'UPDATE_EVENT':
        return {
          ...curState,
          parsedEvents: curState.parsedEvents.map(e => e.id === action.payload.id ? {...e, attr: {...action.payload.newAttribs}} : e),
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
      case 'DO_PARSE':
        if (action.payload.trim() !== '') {
          const parseResult = parseTML(action.payload)
          if (parseResult.transformed) {
            return {
              ...curState,
              textHTML: parseResult.transformed,
              parsedTlinks: [...parseResult.tlinks],
              parsedEvents: [...parseResult.events],
              eventStrings: parseResult.tlinks.map(tlink => {
                if (tlink.warning) {
                  window.alert(`Bad TLINK: ${tlink.e1} ${tlink.rel} ${tlink.e2}`)
                  return []
                }
                return freksa[tlink.rel](tlink.e1, tlink.e2)
              }).filter(l => l.length > 0),
              nextId: getLastId([...parseResult.events], curState.nextId) + 1,
              prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
            }
          } else {
            return {
              ...curState,
              textHTML: parseResult.imported,
              prevStates: [{...curState, prevStates: []}, ...curState.prevStates.slice(0, 50)]
            }
          }
        }
      case 'UNDO': 
        if (curState.prevStates.length > 0) {
          const [cur, ...pre] = curState.prevStates
          return {
            ...cur,
            prevStates: pre
          }
        } else {
          return {
            ...curState
          }
        }
      case 'RESET':
        return init(action.payload)
      default:
        throw new Error('Undefined action type.')
    }
  }, initialState, init)

  useEffect(() => {
    document.addEventListener('keyup', handleKeyboard, false)
      return () => {
        document.removeEventListener('keyup', handleKeyboard, false)
      }
  }, [helpDisplayed, details, state.nextId])

  const handleKeyboard = useCallback(e => {
    const kb = e.key.toLowerCase()
      if (kb === 'e') {
        createMark('EVENT')
      } else if (kb === 't') {
        createMark('TIMEX3')
      } else if (kb === 'u') {
        dispatch({type: 'UNDO'})
      } else if (kb === 's') {
        document.getElementById('dosp').click()
      } else if (kb === '?') {
        setDetails(null)
        setHelpDisplayed(!helpDisplayed)
      } else if (kb === 'escape') {
        setHelpDisplayed(false)
        setDetails(null)
      }
  }, [helpDisplayed, details, state.nextId])

  const dismissOverlay = e => {
    e.stopPropagation()
    if (e.currentTarget === e.target) {
      setDetails(null)
      setHelpDisplayed(false)
    }
  }

  const getNewTLINKs = async () => {
    // const res = await fetch('/api/newTLINKs', {
    const res = await fetch(process.env.NEXT_PUBLIC_NEW_TLINKS_ENDPOINT, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          vocabulary: state.parsedEvents.map(e => e.id),
          strings: state.eventStrings
        }
      })
    })
    const data = await res.json()
    if (data.error) {
      console.error(data)
      window.error(data)
      return []
    }
    return data.tlinks
  }

  const exportTML = async elem => {
    const newTLINKs = await getNewTLINKs()
    const newText = elem.current.cloneNode(true)
    newText.querySelectorAll('.EVENT').forEach(node => {
      const restAttr = Object.entries(state.parsedEvents.find(e => e.id === node.dataset.id).attr).map(a => `${a[0]}="${a[1]}"`).join(' ');
      node.replaceWith(document.createTextNode(`<EVENT eid="${node.dataset.id}" ${restAttr}>${node.textContent}</EVENT>`))
    })
    newText.querySelectorAll('.TIMEX3').forEach(node => {
      const restAttr = Object.entries(state.parsedEvents.find(e => e.id === node.dataset.id).attr).map(a => `${a[0]}="${a[1]}"`).join(' ');
      node.replaceWith(document.createTextNode(`<TIMEX3 tid="${node.dataset.id}" ${restAttr}>${node.textContent}</TIMEX3>`))
    })
    return `<TimeML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd">
${newText.textContent}
${newTLINKs.join('\n')}
</TimeML>`
  }

  const downloadTML = async elem => {
    const dlElem = document.createElement('a')

    dlElem.setAttribute('href', 'data:text/xml;charset=utf-8,' + encodeURIComponent(await exportTML(elem)))
    dlElem.setAttribute('download', 'export.tml')
    dlElem.style.display = 'none'

    document.body.appendChild(dlElem)
    dlElem.click()
    document.body.removeChild(dlElem)
  }

  const createMark = useCallback(tag => {
    if (window.getSelection) {
      const sel = window.getSelection()
      if (sel.type === 'Range' && sel.anchorNode === sel.focusNode && sel.anchorNode.parentElement === document.querySelector('.text pre') && sel.toString().trim() !== '') {
        if (sel.rangeCount) {
          const wrapEl = document.createElement('span')
          wrapEl.classList.add('tml-ev-ano', tag)
          if (tag === 'EVENT') {
            wrapEl.dataset.id = `e${state.nextId}`
            wrapEl.dataset.eventClass = 'OCCURRENCE'
          } else {
            wrapEl.dataset.id = `t${state.nextId}`
            wrapEl.dataset.type = 'DATE'
          }
          wrapEl.textContent = sel.toString()
          const range = sel.getRangeAt(0).cloneRange()
          range.deleteContents()
          range.insertNode(wrapEl)
          sel.removeAllRanges()
          sel.addRange(range)
          dispatch({type: 'ADD_EVENT', payload: {
            event: {
              id: wrapEl.dataset.id,
              type: tag,
              text: wrapEl.textContent,
              elem: wrapEl,
              attr: {}
            },
            newText: sel.anchorNode.parentElement.innerHTML}
          })
        }
      }
    }
  }, [state.nextId])

  const removeMark = useCallback(id => {
    const ev = document.querySelector(`[data-id="${id}"].tml-ev-ano`)
    const textNode = document.createTextNode(ev.textContent)
    const par = ev.parentElement
    ev.replaceWith(textNode)
    par.normalize()
    dispatch({type: 'REMOVE_EVENT', payload: {id, newText: par.innerHTML}})
  })

  const testRelation = async (e1, e2, rel) => {
    // fetch('/api/test', {
    fetch(process.env.NEXT_PUBLIC_TEST_ENDPOINT, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          strings: state.eventStrings,
          e1,
          e2,
          rel
        }
      })
    }).then(response => response.json()).then(data => {
      if (data.error) {
        console.error(data.error)
        window.alert(data.error)
        return
      }
      const { status, strings } = data
      window.alert(`That relation is ${status} according to the knowledge base.${status !== 'contradicted' ? `\nClick 'Add New Relation' to add:\n${strings}` : '\nAdding this relation is not recommended.'}`)
    }).catch(e => console.error(e))
  }

  return (
    <main id="annotate">
      <Head><title>String Temporal Annotation Tool</title></Head>
      {helpDisplayed && <Help extendedRels={extendedRels} setExtendedRels={setExtendedRels} dismiss={dismissOverlay} limit={superposeLimit} setLimit={setSuperposeLimit}/>}
      {details && <Details event={state.parsedEvents.find(e => e.id === details)} dismiss={dismissOverlay} update={(id, newAttribs) => dispatch({type: 'UPDATE_EVENT', payload: {id, newAttribs}})} />}
      {!state.textHTML ? <TextEntry grabParse={val => dispatch({type: 'DO_PARSE', payload: val})}/> : <TextDisplay text={state.textHTML} reset={() => dispatch({type: 'SET_TEXT', payload: ''})} download={downloadTML}/>}
      <div className="panel">
        <p>Select some text, then tag as Event or Time</p>
        <div className="btns">
          <button id="btn-undo" onClick={() => dispatch({type: 'UNDO'})}>Undo</button>
          <button id="btn-reset" onClick={() => window.confirm('Are you sure? No undo.') && dispatch({type: 'RESET', payload: initialState})}>Reset</button>
          <button id="btn-tag-event" onClick={() => createMark('EVENT')}>Tag Event</button>
          <button id="btn-tag-time" onClick={() => createMark('TIMEX3')}>Tag Time</button>
          <button id="btn-help" onClick={() => setHelpDisplayed(true)}>Help</button>
        </div>
        <EventList events={state.parsedEvents} remove={removeMark} edit={setDetails}/>
      </div>
      <StringBank limit={superposeLimit} strings={state.eventStrings} updateStrings={res => dispatch({type: 'SET_STRINGS', payload: [...res]})}/>
      {state.parsedEvents.length > 0 ? <CreateRelation extendedRels={extendedRels} events={state.parsedEvents} addRelation={res => dispatch({type: 'ADD_STRINGS', payload: res})} testRelation={testRelation}/> : <div className="relations"></div>}
    </main>
  )
}
