import { useState, useEffect } from 'react'
import * as freksa from '../fns/freksa'

export default function CreateRelation(props) {
  const [ev1, setEv1] = useState('')
  const [ev2, setEv2] = useState('')
  const [rel, setRel] = useState('')

  const addNewRelation = () => {
    props.addRelation(freksa[rel](ev1, ev2))
  }

  useEffect(() => {
    setEv1('')
    setEv2('')
    setRel('')
  }, [props.extendedRels])

  return (
    <div className="relations">
      <ul>
        <li>
        <label htmlFor="ev1-select">Event 1:</label> <select id="ev1-select" value={ev1} className="ev1" onChange={e => setEv1(e.currentTarget.value)}>
          {ev1 === '' && <option disabled value=''>Select Event</option>}
          {props.events.map(ev => <option key={`ev1-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select>
        </li>
        <li>
        <label htmlFor="rel-select">Rel:</label> <select value={rel} className="rel" onChange={e => setRel(e.currentTarget.value)} disabled={ev1 === ev2 || ev1 === '' || ev2 === ''}>
          {rel === '' && <option disabled value=''>Select Relation</option>}
          <option value="b">BEFORE (|{ev1}||{ev2}|)</option>
          <option value="bi">AFTER (|{ev2}||{ev1}|)</option>
          <option value="m">IBEFORE (|{ev1}|{ev2}|)</option>
          {/* <option value="m">MEETING (|{ev1}|{ev2}|)</option> */}
          <option value="mi">IAFTER (|{ev2}|{ev1}|)</option>
          {/* <option value="mi">MET BY (|{ev2}|{ev1}|)</option> */}
          <option value="s">BEGINS (|{ev1},{ev2}|{ev2}|)</option>
          {/* <option value="s">STARTING (|{ev1},{ev2}|{ev2}|)</option> */}
          <option value="si">BEGUN_BY (|{ev1},{ev2}|{ev1}|)</option>
          {/* <option value="si">STARTED BY (|{ev1},{ev2}|{ev1}|)</option> */}
          <option value="f">ENDS (|{ev2}|{ev1},{ev2}|)</option>
          {/* <option value="f">FINISHING (|{ev2}|{ev1},{ev2}|)</option> */}
          <option value="fi">ENDED_BY (|{ev1}|{ev1},{ev2}|)</option>
          {/* <option value="fi">FINISHED BY (|{ev1}|{ev1},{ev2}|)</option> */}
          <option value="di">INCLUDES (|{ev1}|{ev1},{ev2}|{ev1}|)</option>
          <option value="d">IS_INCLUDED (|{ev2}|{ev1},{ev2}|{ev2}|)</option>
          <option value="d">DURING (|{ev2}|{ev1},{ev2}|{ev2}|)</option>
          <option value="di">DURING_INV (|{ev1}|{ev1},{ev2}|{ev1}|)</option>
          {/* <option value="di">CONTAINING (|{ev1}|{ev1},{ev2}|{ev1}|)</option> */}
          {/* <option value="d">CONTAINED BY (|{ev2}|{ev1},{ev2}|{ev2}|)</option> */}
          {<option value="o">OVERLAPS (|{ev1}|{ev1},{ev2}|{ev2}|)</option>}
          {<option value="oi">OVERLAPPED BY (|{ev2}|{ev1},{ev2}|{ev1}|)</option>}
          <option value="e">SIMULTANEOUS (|{ev1},{ev2}|)</option>
          <option value="e">IDENTITY (|{ev1},{ev2}|)</option>
          {props.extendedRels && <option value="ol">OLDER</option>}
          {props.extendedRels && <option value="yo">YOUNGER</option>}
          {props.extendedRels && <option value="hh">HEAD_TO_HEAD</option>}
          {props.extendedRels && <option value="tt">TAIL_TO_TAIL</option>}
          {props.extendedRels && <option value="sv">SURVIVES</option>}
          {props.extendedRels && <option value="sb">SURVIVED_BY</option>}
          {props.extendedRels && <option value="pr">PRECEDES</option>}
          {props.extendedRels && <option value="sd">SUCCEEDS</option>}
          {props.extendedRels && <option value="bd">BORN_BEFORE_DEATH</option>}
          {props.extendedRels && <option value="db">DIED_AFTER_BIRTH</option>}
          {props.extendedRels && <option value="ct">CONTEMPORARY</option>}
          {props.extendedRels && <option value="ob">OLDER_SURVIVED_BY</option>}
          {props.extendedRels && <option value="oc">OLDER_CONTEMPORARY</option>}
          {props.extendedRels && <option value="sc">SURVIVING_CONTEMPORARY</option>}
          {props.extendedRels && <option value="bc">SURVIVED_BY_CONTEMPORARY</option>}
          {props.extendedRels && <option value="yc">YOUNGER_CONTEMPORARY</option>}
          {props.extendedRels && <option value="ys">YOUNGER_SURVIVES</option>}
        </select>
        </li>
        <li>
        <label htmlFor="ev2-select">Event 2:</label> <select value={ev2} className="ev2" onChange={e => setEv2(e.currentTarget.value)}>
          {ev2 === '' && <option disabled value=''>Select Event</option>}
          {props.events.map(ev => <option key={`ev2-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select>
        </li>
      </ul>
      <button id="testRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={() => props.testRelation(ev1, ev2, rel)}>Test Relation</button>
      <button id="createRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={addNewRelation}>Add New Relation</button>
      <button id="tryFindRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === ''} onClick={() => props.tryFindRelation(ev1, ev2)}>Try Find Relation</button>
    </div>
  )
}
